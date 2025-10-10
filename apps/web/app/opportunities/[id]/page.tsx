import { createClient } from '@supabase/supabase-js'
import { notFound } from 'next/navigation'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

interface PageProps {
  params: {
    id: string
  }
}

export default async function OpportunityDetailPage({ params }: PageProps) {
  const { data: opportunity, error } = await supabase
    .from('funding_opportunities')
    .select('*')
    .eq('opportunity_id', params.id)
    .single()

  if (error || !opportunity) {
    notFound()
  }

  return (
    <div className="min-h-screen bg-neutral-50">
      {/* Header */}
      <header className="bg-white border-b border-neutral-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <a href="/" className="flex items-center gap-3">
              <div className="h-8 w-8 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg"></div>
              <span className="text-xl font-bold text-neutral-900">GovFunding</span>
            </a>
          </div>
          <nav className="flex items-center gap-6">
            <a href="/dashboard" className="text-neutral-700 hover:text-primary-600 transition">Dashboard</a>
            <a href="/search" className="text-neutral-700 hover:text-primary-600 transition">Search</a>
            <button className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition">
              Ask AI
            </button>
          </nav>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-6 py-8">
        {/* Breadcrumb */}
        <div className="flex items-center gap-2 text-sm text-neutral-600 mb-6">
          <a href="/dashboard" className="hover:text-primary-600">Dashboard</a>
          <span>/</span>
          <span className="text-neutral-900">{opportunity.title}</span>
        </div>

        {/* Header Card */}
        <div className="bg-white rounded-xl border border-neutral-200 p-8 mb-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <h1 className="text-3xl font-bold text-neutral-900 mb-3">
                {opportunity.title}
              </h1>
              <div className="flex items-center gap-3">
                <span className="inline-flex items-center px-4 py-1.5 bg-primary-50 text-primary-700 rounded-full text-sm font-medium">
                  {opportunity.agency_name}
                </span>
                {opportunity.deadline_status && (
                  <span
                    className={`inline-flex items-center px-4 py-1.5 rounded-full text-sm font-medium ${
                      opportunity.deadline_status === 'open'
                        ? 'bg-green-50 text-green-700'
                        : opportunity.deadline_status === 'closing_soon'
                        ? 'bg-orange-50 text-orange-700'
                        : 'bg-neutral-100 text-neutral-600'
                    }`}
                  >
                    {opportunity.deadline_status === 'open' && '✓ Open'}
                    {opportunity.deadline_status === 'closing_soon' && '⚠ Closing Soon'}
                    {opportunity.deadline_status === 'closed' && '✕ Closed'}
                    {opportunity.deadline_status === 'unknown' && '? Unknown'}
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Key Details Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-6 pt-6 border-t border-neutral-200">
            <div>
              <div className="text-sm text-neutral-600 mb-1">Award Range</div>
              <div className="text-lg font-semibold text-neutral-900">
                {opportunity.award_floor && opportunity.award_ceiling
                  ? `$${(opportunity.award_floor / 1000).toFixed(0)}K - $${(opportunity.award_ceiling / 1000).toFixed(0)}K`
                  : opportunity.award_ceiling
                  ? `Up to $${(opportunity.award_ceiling / 1000).toFixed(0)}K`
                  : 'TBD'}
              </div>
            </div>

            <div>
              <div className="text-sm text-neutral-600 mb-1">Deadline</div>
              <div className="text-lg font-semibold text-neutral-900">
                {opportunity.close_date
                  ? new Date(opportunity.close_date).toLocaleDateString('en-US', {
                      month: 'short',
                      day: 'numeric',
                      year: 'numeric',
                    })
                  : 'Not specified'}
              </div>
            </div>

            <div>
              <div className="text-sm text-neutral-600 mb-1">Posted</div>
              <div className="text-lg font-semibold text-neutral-900">
                {opportunity.post_date
                  ? new Date(opportunity.post_date).toLocaleDateString('en-US', {
                      month: 'short',
                      day: 'numeric',
                      year: 'numeric',
                    })
                  : 'Unknown'}
              </div>
            </div>

            <div>
              <div className="text-sm text-neutral-600 mb-1">Opportunity ID</div>
              <div className="text-sm font-mono text-neutral-900 truncate">
                {opportunity.opportunity_id}
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3 mt-6 pt-6 border-t border-neutral-200">
            <button className="flex-1 px-6 py-3 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition font-medium">
              Apply on Grants.gov →
            </button>
            <button className="px-6 py-3 border-2 border-primary-500 text-primary-600 rounded-lg hover:bg-primary-50 transition font-medium">
              Bookmark
            </button>
            <button className="px-6 py-3 border-2 border-neutral-300 text-neutral-700 rounded-lg hover:bg-neutral-50 transition font-medium">
              Share
            </button>
          </div>
        </div>

        {/* Summary Section */}
        {opportunity.summary && (
          <div className="bg-white rounded-xl border border-neutral-200 p-8 mb-6">
            <h2 className="text-xl font-bold text-neutral-900 mb-4">Summary</h2>
            <p className="text-neutral-700 leading-relaxed whitespace-pre-wrap">
              {opportunity.summary}
            </p>
          </div>
        )}

        {/* Description Section */}
        {opportunity.description && (
          <div className="bg-white rounded-xl border border-neutral-200 p-8 mb-6">
            <h2 className="text-xl font-bold text-neutral-900 mb-4">Full Description</h2>
            <div className="prose prose-neutral max-w-none">
              <p className="text-neutral-700 leading-relaxed whitespace-pre-wrap">
                {opportunity.description}
              </p>
            </div>
          </div>
        )}

        {/* Eligibility Section */}
        {opportunity.eligibility && (
          <div className="bg-white rounded-xl border border-neutral-200 p-8 mb-6">
            <h2 className="text-xl font-bold text-neutral-900 mb-4">Eligibility Requirements</h2>
            <div className="text-neutral-700 leading-relaxed whitespace-pre-wrap">
              {opportunity.eligibility}
            </div>
          </div>
        )}

        {/* AI Q&A Section */}
        <div className="bg-gradient-to-br from-primary-50 to-white rounded-xl border border-primary-200 p-8 mb-6">
          <div className="flex items-start gap-4">
            <div className="flex-shrink-0 w-12 h-12 bg-primary-500 rounded-lg flex items-center justify-center text-2xl">
              🤖
            </div>
            <div className="flex-1">
              <h2 className="text-xl font-bold text-neutral-900 mb-2">Ask AI About This Grant</h2>
              <p className="text-neutral-600 mb-4">
                Have questions about eligibility, requirements, or application process? Ask our AI assistant!
              </p>
              <button className="px-6 py-3 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition font-medium">
                Start Conversation
              </button>
            </div>
          </div>
        </div>

        {/* Additional Information */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Contact Information */}
          {opportunity.contact_info && (
            <div className="bg-white rounded-xl border border-neutral-200 p-6">
              <h3 className="text-lg font-bold text-neutral-900 mb-3">Contact Information</h3>
              <div className="text-neutral-700 text-sm whitespace-pre-wrap">
                {opportunity.contact_info}
              </div>
            </div>
          )}

          {/* Related Links */}
          <div className="bg-white rounded-xl border border-neutral-200 p-6">
            <h3 className="text-lg font-bold text-neutral-900 mb-3">Related Links</h3>
            <ul className="space-y-2">
              <li>
                <a
                  href={`https://grants.gov/search-results-detail/${opportunity.opportunity_id}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary-600 hover:underline text-sm"
                >
                  View on Grants.gov →
                </a>
              </li>
              <li>
                <a href="#" className="text-primary-600 hover:underline text-sm">
                  Download Full Solicitation (PDF) →
                </a>
              </li>
              <li>
                <a href="#" className="text-primary-600 hover:underline text-sm">
                  View Similar Opportunities →
                </a>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
