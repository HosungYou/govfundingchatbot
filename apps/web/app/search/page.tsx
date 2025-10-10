import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

interface SearchParams {
  searchParams: {
    q?: string
    agency?: string
    status?: string
  }
}

export default async function SearchPage({ searchParams }: SearchParams) {
  const query = searchParams.q || ''
  const agency = searchParams.agency || ''
  const status = searchParams.status || 'open'

  // Build Supabase query
  let supabaseQuery = supabase
    .from('funding_opportunities')
    .select('*')

  // Apply filters
  if (status && status !== 'all') {
    supabaseQuery = supabaseQuery.eq('deadline_status', status)
  }

  if (agency) {
    supabaseQuery = supabaseQuery.eq('agency_name', agency)
  }

  if (query) {
    supabaseQuery = supabaseQuery.textSearch('title', query, {
      type: 'websearch',
      config: 'english',
    })
  }

  // Execute query
  const { data: opportunities, error } = await supabaseQuery
    .order('post_date', { ascending: false })
    .limit(50)

  // Get unique agencies for filter
  const { data: agencies } = await supabase
    .from('funding_opportunities')
    .select('agency_name')
    .not('agency_name', 'is', null)

  const uniqueAgencies = Array.from(new Set(agencies?.map(a => a.agency_name) || []))

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
            <a href="/search" className="text-primary-600 font-medium">Search</a>
            <button className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition">
              Ask AI
            </button>
          </nav>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Filters Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl border border-neutral-200 p-6 sticky top-24">
              <h2 className="text-lg font-bold text-neutral-900 mb-6">Filters</h2>

              {/* Search Input */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-neutral-700 mb-2">
                  Keyword Search
                </label>
                <form action="/search" method="get">
                  <input
                    type="text"
                    name="q"
                    defaultValue={query}
                    placeholder="e.g., climate change, AI, biotech..."
                    className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  />
                  <input type="hidden" name="agency" value={agency} />
                  <input type="hidden" name="status" value={status} />
                  <button
                    type="submit"
                    className="w-full mt-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition"
                  >
                    Search
                  </button>
                </form>
              </div>

              {/* Status Filter */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-neutral-700 mb-2">
                  Status
                </label>
                <form action="/search" method="get">
                  <input type="hidden" name="q" value={query} />
                  <input type="hidden" name="agency" value={agency} />
                  <select
                    name="status"
                    defaultValue={status}
                    onChange={(e) => (e.target.form as HTMLFormElement)?.submit()}
                    className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  >
                    <option value="all">All Statuses</option>
                    <option value="open">Open</option>
                    <option value="closing_soon">Closing Soon</option>
                    <option value="closed">Closed</option>
                  </select>
                </form>
              </div>

              {/* Agency Filter */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-neutral-700 mb-2">
                  Agency
                </label>
                <form action="/search" method="get">
                  <input type="hidden" name="q" value={query} />
                  <input type="hidden" name="status" value={status} />
                  <select
                    name="agency"
                    defaultValue={agency}
                    onChange={(e) => (e.target.form as HTMLFormElement)?.submit()}
                    className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  >
                    <option value="">All Agencies</option>
                    {uniqueAgencies.map(ag => (
                      <option key={ag} value={ag}>{ag}</option>
                    ))}
                  </select>
                </form>
              </div>

              {/* Clear Filters */}
              <a
                href="/search"
                className="block text-center px-4 py-2 text-sm text-neutral-600 hover:text-primary-600 transition"
              >
                Clear All Filters
              </a>
            </div>
          </div>

          {/* Results */}
          <div className="lg:col-span-3">
            {/* Results Header */}
            <div className="mb-6">
              <h1 className="text-3xl font-bold text-neutral-900 mb-2">
                {query ? `Search Results for "${query}"` : 'All Opportunities'}
              </h1>
              <p className="text-neutral-600">
                Found {opportunities?.length || 0} opportunities
                {agency && ` from ${agency}`}
                {status !== 'all' && ` (${status})`}
              </p>
            </div>

            {/* Error State */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                <p className="text-red-800 font-medium">Error loading results</p>
                <p className="text-red-600 text-sm mt-1">{error.message}</p>
              </div>
            )}

            {/* Empty State */}
            {!opportunities || opportunities.length === 0 ? (
              <div className="bg-white rounded-xl border border-neutral-200 p-12 text-center">
                <div className="text-6xl mb-4">🔍</div>
                <h2 className="text-xl font-bold text-neutral-900 mb-2">No Results Found</h2>
                <p className="text-neutral-600 mb-6">
                  {query
                    ? `No opportunities match "${query}". Try different keywords or filters.`
                    : 'No opportunities available with the selected filters.'}
                </p>
                <a href="/search" className="text-primary-600 hover:underline font-medium">
                  Clear filters and try again →
                </a>
              </div>
            ) : (
              /* Results List */
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
      </div>
    </div>
  )
}
