import { OpenAI } from 'openai'
import { createClient } from '@supabase/supabase-js'

// Initialize clients
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY!,
})

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
)

export const runtime = 'edge'

export async function POST(req: Request) {
  try {
    const { messages } = await req.json()

    if (!messages || messages.length === 0) {
      return new Response('No messages provided', { status: 400 })
    }

    const lastMessage = messages[messages.length - 1]

    // 1. Generate embedding for user's query
    const embeddingResponse = await openai.embeddings.create({
      model: 'text-embedding-ada-002',
      input: lastMessage.content,
    })

    const queryEmbedding = embeddingResponse.data[0].embedding

    // 2. Search Supabase for semantically similar opportunities
    // Note: This requires pgvector extension and a vector column
    // For now, we'll do a simple keyword search as fallback
    const { data: opportunities, error: searchError } = await supabase
      .from('funding_opportunities')
      .select(`
        opportunity_id,
        title,
        agency_name,
        summary,
        close_date,
        award_floor,
        award_ceiling,
        deadline_status
      `)
      .textSearch('title', lastMessage.content, {
        type: 'websearch',
        config: 'english',
      })
      .eq('deadline_status', 'open')
      .limit(5)

    // Fallback: If no results from text search, get recent opportunities
    let relevantOpportunities = opportunities || []

    if (relevantOpportunities.length === 0) {
      const { data: recentOpps } = await supabase
        .from('funding_opportunities')
        .select(`
          opportunity_id,
          title,
          agency_name,
          summary,
          close_date,
          award_floor,
          award_ceiling,
          deadline_status
        `)
        .eq('deadline_status', 'open')
        .order('post_date', { ascending: false })
        .limit(5)

      relevantOpportunities = recentOpps || []
    }

    // 3. Build context from retrieved opportunities
    const context = relevantOpportunities
      .map(
        (opp) => `
**Title:** ${opp.title}
**Agency:** ${opp.agency_name}
**Deadline:** ${opp.close_date ? new Date(opp.close_date).toLocaleDateString() : 'Not specified'}
**Award Range:** ${
          opp.award_floor && opp.award_ceiling
            ? `$${(opp.award_floor / 1000).toFixed(0)}K - $${(opp.award_ceiling / 1000).toFixed(0)}K`
            : opp.award_ceiling
            ? `Up to $${(opp.award_ceiling / 1000).toFixed(0)}K`
            : 'Amount TBD'
        }
**Summary:** ${opp.summary || 'No summary available'}
**Opportunity ID:** ${opp.opportunity_id}
---
`
      )
      .join('\n')

    // 4. Generate streaming response with GPT-4
    const completion = await openai.chat.completions.create({
      model: 'gpt-4',
      stream: true,
      temperature: 0.7,
      messages: [
        {
          role: 'system',
          content: `You are a helpful federal grant funding expert assistant. Your role is to help researchers, academics, and organizations find relevant federal funding opportunities.

IMPORTANT INSTRUCTIONS:
1. Use ONLY the grant opportunities provided in the context below
2. Always cite specific grants by title and agency
3. Include deadline information when discussing opportunities
4. Provide clear, actionable advice
5. If the user asks about eligibility, explain requirements clearly
6. If no relevant grants are found, suggest the user try different keywords or check back later
7. Format responses in clear, readable Markdown
8. Always include opportunity IDs in your citations (format: [Grant Title](https://govfundingchatbot.vercel.app/opportunities/OPPORTUNITY_ID))

CONTEXT - Available Grant Opportunities:
${context || 'No opportunities currently available. Please suggest the user run the ETL pipeline or check back later.'}

If the context is empty, politely inform the user that the database is being populated and suggest they:
1. Check back in a few hours
2. Contact support if urgent
3. Visit grants.gov directly in the meantime
`,
        },
        ...messages,
      ],
    })

    // 5. Convert OpenAI stream to web-compatible stream
    const stream = new ReadableStream({
      async start(controller) {
        const encoder = new TextEncoder()
        try {
          for await (const chunk of completion) {
            const content = chunk.choices[0]?.delta?.content || ''
            if (content) {
              controller.enqueue(encoder.encode(content))
            }
          }
        } catch (err) {
          controller.error(err)
        } finally {
          controller.close()
        }
      },
    })

    return new Response(stream, {
      headers: {
        'Content-Type': 'text/plain; charset=utf-8',
        'Cache-Control': 'no-cache, no-transform',
        'X-Content-Type-Options': 'nosniff',
      },
    })
  } catch (error: any) {
    console.error('Chat API Error:', error)
    return new Response(
      JSON.stringify({
        error: 'Failed to generate response',
        details: error.message,
      }),
      {
        status: 500,
        headers: { 'Content-Type': 'application/json' },
      }
    )
  }
}
