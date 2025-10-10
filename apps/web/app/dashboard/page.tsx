import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

interface Opportunity {
  opportunity_id: string
  title: string
  agency_name: string
  close_date: string | null
  award_floor: number | null
  award_ceiling: number | null
  deadline_status: string
  summary: string | null
  post_date: string | null
}

export default async function Dashboard() {
  // Fetch recent opportunities from Supabase
  const { data: opportunities, error } = await supabase
    .from('funding_opportunities')
    .select(`
      opportunity_id,
      title,
      agency_name,
      close_date,
      award_floor,
      award_ceiling,
      deadline_status,
      summary,
      post_date
    `)
    .order('post_date', { ascending: false })
    .limit(20)

  // Fetch statistics
  const { count: totalCount } = await supabase
    .from('funding_opportunities')
    .select('*', { count: 'exact', head: true })
    .eq('deadline_status', 'open')

  const { data: fundingData } = await supabase
    .from('funding_opportunities')
    .select('award_ceiling')
    .eq('deadline_status', 'open')

  const totalFunding = fundingData?.reduce((sum, opp) => sum + (opp.award_ceiling || 0), 0) || 0

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
            <a href="/dashboard" className="text-primary-600 font-medium">Dashboard</a>
            <a href="/search" className="text-neutral-700 hover:text-primary-600 transition">Search</a>
            <button className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition">
              Ask AI
            </button>
          </nav>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded-xl border border-neutral-200 shadow-sm">
            <div className="text-sm text-neutral-600 mb-1">Active Opportunities</div>
            <div className="text-3xl font-bold text-neutral-900">
              {totalCount?.toLocaleString() || '0'}
            </div>
            <div className="text-xs text-green-600 mt-1">↑ Updated daily</div>
          </div>

          <div className="bg-white p-6 rounded-xl border border-neutral-200 shadow-sm">
            <div className="text-sm text-neutral-600 mb-1">Total Available Funding</div>
            <div className="text-3xl font-bold text-neutral-900">
              ${((totalFunding || 0) / 1e9).toFixed(1)}B
            </div>
            <div className="text-xs text-neutral-500 mt-1">Across all agencies</div>
          </div>

          <div className="bg-white p-6 rounded-xl border border-neutral-200 shadow-sm">
            <div className="text-sm text-neutral-600 mb-1">AI Search Time</div>
            <div className="text-3xl font-bold text-neutral-900">&lt;2s</div>
            <div className="text-xs text-primary-600 mt-1">Average response time</div>
          </div>
        </div>

        {/* Page Title */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-neutral-900 mb-2">Recent Opportunities</h1>
          <p className="text-neutral-600">Latest federal funding opportunities from NSF and Grants.gov</p>
        </div>

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-800 font-medium">Error loading opportunities</p>
            <p className="text-red-600 text-sm mt-1">{error.message}</p>
          </div>
        )}

        {/* Empty State */}
        {!opportunities || opportunities.length === 0 ? (
          <div className="bg-white rounded-xl border border-neutral-200 p-12 text-center">
            <div className="text-6xl mb-4">🔍</div>
            <h2 className="text-xl font-bold text-neutral-900 mb-2">No Opportunities Yet</h2>
            <p className="text-neutral-600 mb-6">
              Run the ETL pipeline to populate the database with federal grant opportunities.
            </p>
            <code className="bg-neutral-100 px-4 py-2 rounded text-sm">
              cd apps/etl && PYTHONPATH=../.. python3 pipeline.py
            </code>
          </div>
        ) : (
          /* Opportunity Cards */
          <div className="grid gap-4">
            {opportunities.map((opp) => (
              <a
                key={opp.opportunity_id}
                href={`/opportunities/${opp.opportunity_id}`}
                className="block bg-white rounded-xl border border-neutral-200 p-6 hover:shadow-lg transition group"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-neutral-900 group-hover:text-primary-600 transition line-clamp-2">
                      {opp.title}
                    </h3>
                    <div className="flex items-center gap-3 mt-2">
                      <span className="inline-flex items-center px-3 py-1 bg-primary-50 text-primary-700 rounded-full text-xs font-medium">
                        {opp.agency_name}
                      </span>
                      {opp.deadline_status && (
                        <span
                          className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${
                            opp.deadline_status === 'open'
                              ? 'bg-green-50 text-green-700'
                              : opp.deadline_status === 'closing_soon'
                              ? 'bg-orange-50 text-orange-700'
                              : 'bg-neutral-100 text-neutral-600'
                          }`}
                        >
                          {opp.deadline_status === 'open' && '✓ Open'}
                          {opp.deadline_status === 'closing_soon' && '⚠ Closing Soon'}
                          {opp.deadline_status === 'closed' && '✕ Closed'}
                          {opp.deadline_status === 'unknown' && '? Unknown'}
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="text-right ml-6">
                    {opp.award_floor && opp.award_ceiling ? (
                      <>
                        <div className="text-sm text-neutral-600">Award Range</div>
                        <div className="text-lg font-semibold text-neutral-900">
                          ${(opp.award_floor / 1000).toFixed(0)}K - ${(opp.award_ceiling / 1000).toFixed(0)}K
                        </div>
                      </>
                    ) : opp.award_ceiling ? (
                      <>
                        <div className="text-sm text-neutral-600">Up to</div>
                        <div className="text-lg font-semibold text-neutral-900">
                          ${(opp.award_ceiling / 1000).toFixed(0)}K
                        </div>
                      </>
                    ) : (
                      <div className="text-sm text-neutral-500">Amount TBD</div>
                    )}
                  </div>
                </div>

                {opp.summary && (
                  <p className="text-neutral-600 text-sm line-clamp-2 mb-3">{opp.summary}</p>
                )}

                <div className="flex items-center justify-between text-sm">
                  <div className="text-neutral-500">
                    {opp.close_date ? (
                      <>
                        <span className="font-medium">Deadline:</span>{' '}
                        {new Date(opp.close_date).toLocaleDateString('en-US', {
                          month: 'short',
                          day: 'numeric',
                          year: 'numeric',
                        })}
                      </>
                    ) : (
                      <span className="text-neutral-400">No deadline specified</span>
                    )}
                  </div>
                  <div className="text-primary-600 font-medium group-hover:underline">
                    View Details →
                  </div>
                </div>
              </a>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
