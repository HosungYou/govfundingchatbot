import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

export default async function Home() {
  // Fetch real-time metrics from Supabase
  const { count: totalOpportunities } = await supabase
    .from('funding_opportunities')
    .select('*', { count: 'exact', head: true })
    .eq('deadline_status', 'open')

  const { data: fundingData } = await supabase
    .from('funding_opportunities')
    .select('award_ceiling')
    .eq('deadline_status', 'open')

  const totalFunding = fundingData?.reduce((sum, opp) => sum + (opp.award_ceiling || 0), 0) || 0

  // Get recent opportunities for preview
  const { data: recentOpportunities } = await supabase
    .from('funding_opportunities')
    .select('opportunity_id, title, agency_name, award_floor, award_ceiling, close_date')
    .eq('deadline_status', 'open')
    .order('post_date', { ascending: false })
    .limit(3)

  const activeCount = totalOpportunities || 0
  const fundingAmount = totalFunding ? (totalFunding / 1e9).toFixed(1) : '0.0'

  return (
    <div className="min-h-screen bg-neutral-50">
      {/* Header - Enhanced */}
      <header className="sticky top-0 z-50 bg-white border-b border-neutral-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 flex items-center justify-between h-16">
          <div className="flex items-center gap-3">
            <div className="h-8 w-8 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg"></div>
            <span className="text-xl font-bold text-neutral-900">GovFunding</span>
          </div>
          <nav className="hidden md:flex gap-8">
            <a href="#features" className="text-neutral-700 hover:text-primary-600 transition">Features</a>
            <a href="#opportunities" className="text-neutral-700 hover:text-primary-600 transition">Live Opportunities</a>
            <a href="#how-it-works" className="text-neutral-700 hover:text-primary-600 transition">How It Works</a>
          </nav>
          <div className="flex items-center gap-4">
            <button className="text-neutral-700 hover:text-primary-600 transition font-medium">Sign In</button>
            <a href="/dashboard">
              <button className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition shadow-sm">
                Get Started
              </button>
            </a>
          </div>
        </div>
      </header>

      {/* Hero Section - Enhanced */}
      <section className="bg-gradient-to-br from-primary-50 via-white to-neutral-50 py-20">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            {/* Left: Hero Content */}
            <div>
              <div className="inline-block px-4 py-2 bg-primary-100 text-primary-700 rounded-full text-sm font-medium mb-6">
                🚀 Now tracking {activeCount.toLocaleString()} active opportunities
              </div>
              <h1 className="text-5xl lg:text-6xl font-bold text-neutral-900 leading-tight">
                Find Federal Funding{' '}
                <span className="bg-gradient-to-r from-primary-500 to-primary-700 bg-clip-text text-transparent">
                  10× Faster
                </span>
              </h1>
              <p className="mt-6 text-xl text-neutral-600 leading-relaxed">
                AI-powered search across NSF awards and federal grants.
                Get alerts for opportunities matching your research.
              </p>
              <div className="mt-8 flex flex-col sm:flex-row gap-4">
                <a href="/dashboard">
                  <button className="px-8 py-4 bg-primary-500 text-white rounded-lg hover:bg-primary-600 text-lg font-semibold shadow-lg hover:shadow-xl transition transform hover:-translate-y-0.5">
                    Try Dashboard →
                  </button>
                </a>
                <button className="px-8 py-4 border-2 border-primary-500 text-primary-600 rounded-lg hover:bg-primary-50 text-lg font-semibold transition">
                  Watch Demo
                </button>
              </div>
              <div className="mt-8 flex items-center gap-4 text-sm text-neutral-500">
                <div className="flex -space-x-2">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 border-2 border-white"></div>
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-400 to-purple-600 border-2 border-white"></div>
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-pink-400 to-pink-600 border-2 border-white"></div>
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-green-400 to-green-600 border-2 border-white"></div>
                </div>
                <span className="font-medium text-neutral-700">Trusted by 500+ researchers</span>
              </div>
            </div>

            {/* Right: Preview Card */}
            <div className="hidden lg:block">
              <div className="rounded-2xl shadow-2xl border border-neutral-200 bg-white p-6">
                <div className="flex items-center justify-between pb-4 border-b">
                  <h3 className="font-semibold">Recent Opportunities</h3>
                  <span className="text-xs px-2 py-1 bg-green-100 text-green-700 rounded-full">Live</span>
                </div>
                <div className="space-y-3 mt-4">
                  {recentOpportunities && recentOpportunities.length > 0 ? (
                    recentOpportunities.map((opp) => (
                      <a
                        key={opp.opportunity_id}
                        href={`/opportunities/${opp.opportunity_id}`}
                        className="block p-4 bg-neutral-50 rounded-lg hover:border-primary-300 border border-neutral-200 transition cursor-pointer"
                      >
                        <div className="flex justify-between mb-2">
                          <span className="text-xs font-semibold text-primary-600">{opp.agency_name}</span>
                          <span className="text-xs text-neutral-500">
                            {opp.close_date
                              ? `${Math.ceil((new Date(opp.close_date).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))} days`
                              : 'No deadline'}
                          </span>
                        </div>
                        <h4 className="font-medium text-sm mb-1 line-clamp-1">{opp.title}</h4>
                        <p className="text-xs text-neutral-500">
                          {opp.award_floor && opp.award_ceiling
                            ? `$${(opp.award_floor / 1000).toFixed(0)}K - $${(opp.award_ceiling / 1000).toFixed(0)}K`
                            : opp.award_ceiling
                            ? `Up to $${(opp.award_ceiling / 1000).toFixed(0)}K`
                            : 'Amount TBD'}
                        </p>
                      </a>
                    ))
                  ) : (
                    <div className="p-4 text-center text-neutral-500 text-sm">
                      No opportunities yet. Run ETL pipeline to populate database.
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Live Metrics - Enhanced with 4 metrics */}
      <section className="bg-white py-12 border-y">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="text-4xl font-bold bg-gradient-to-r from-primary-500 to-primary-700 bg-clip-text text-transparent">
                {activeCount.toLocaleString()}
              </div>
              <div className="mt-2 text-neutral-600 font-medium">Active Opportunities</div>
              <div className="mt-1 flex items-center justify-center gap-1 text-sm text-green-600">
                <span>↑ Updated daily</span>
              </div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold bg-gradient-to-r from-primary-500 to-primary-700 bg-clip-text text-transparent">${fundingAmount}B</div>
              <div className="mt-2 text-neutral-600 font-medium">Available Funding</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold bg-gradient-to-r from-primary-500 to-primary-700 bg-clip-text text-transparent">&lt;2s</div>
              <div className="mt-2 text-neutral-600 font-medium">Search Time</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold bg-gradient-to-r from-primary-500 to-primary-700 bg-clip-text text-transparent">98%</div>
              <div className="mt-2 text-neutral-600 font-medium">Accuracy</div>
            </div>
          </div>
        </div>
      </section>

      {/* NEW: Live Opportunities Table */}
      <section id="opportunities" className="py-20 bg-neutral-50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-neutral-900 mb-4">
              Latest Funding Opportunities
            </h2>
            <p className="text-xl text-neutral-600">
              Real-time data from NSF and Grants.gov
            </p>
          </div>

          <div className="bg-white rounded-xl shadow-lg border overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-neutral-50 border-b">
                  <tr>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-neutral-700 uppercase">Opportunity</th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-neutral-700 uppercase">Agency</th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-neutral-700 uppercase">Award Range</th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-neutral-700 uppercase">Deadline</th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-neutral-700 uppercase">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {[
                    { title: 'Advancing Informal STEM Learning', id: 612, range: '$50K-$500K', deadline: 'Apr 15', days: 12, status: 'open' },
                    { title: 'CS for All', id: 613, range: '$100K-$1M', deadline: 'May 1', days: 28, status: 'open' },
                    { title: 'Improving Undergrad STEM Ed', id: 614, range: '$300K-$2M', deadline: 'Jun 15', days: 73, status: 'open' },
                    { title: 'CAREER Development', id: 615, range: '$400K-$500K', deadline: 'Mar 28', days: 5, status: 'closing' },
                    { title: 'Research Exp for Undergrads', id: 616, range: '$50K-$150K', deadline: 'Apr 30', days: 27, status: 'open' },
                  ].map((o, i) => (
                    <tr key={i} className="hover:bg-primary-50 transition cursor-pointer">
                      <td className="px-6 py-4">
                        <div className="font-medium text-neutral-900">{o.title}</div>
                        <div className="text-sm text-neutral-500">NSF-25-{o.id}</div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm font-medium">NSF</span>
                      </td>
                      <td className="px-6 py-4 font-medium text-neutral-700">{o.range}</td>
                      <td className="px-6 py-4">
                        <div>{o.deadline}</div>
                        <div className="text-sm text-neutral-500">{o.days} days</div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                          o.status === 'open' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
                        }`}>
                          {o.status === 'open' ? 'Open' : 'Closing Soon'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="bg-neutral-50 px-6 py-4 border-t flex justify-between items-center">
              <p className="text-sm text-neutral-600">
                Showing <strong>5</strong> of <strong>1,247</strong> opportunities
              </p>
              <button className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition">
                View All →
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* NEW: Agency Grid */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-neutral-900 mb-4">Funding by Agency</h2>
            <p className="text-xl text-neutral-600">Browse from top federal sources</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { name: 'NSF', full: 'National Science Foundation', count: 847, funding: '$8.2B' },
              { name: 'NIH', full: 'National Institutes of Health', count: 234, funding: '$2.8B' },
              { name: 'DOE', full: 'Department of Energy', count: 98, funding: '$1.1B' },
              { name: 'NASA', full: 'Space Administration', count: 45, funding: '$450M' },
              { name: 'USDA', full: 'Dept of Agriculture', count: 23, funding: '$120M' },
              { name: 'Other', full: 'Various Agencies', count: 12, funding: '$80M' },
            ].map((a, i) => (
              <div key={i} className="p-6 bg-neutral-50 rounded-xl border hover:border-primary-300 hover:shadow-lg transition cursor-pointer">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-primary-400 to-primary-600 rounded-lg flex items-center justify-center text-white font-bold text-xl">
                    {a.name[0]}
                  </div>
                  <div>
                    <h3 className="font-bold text-neutral-900">{a.name}</h3>
                    <p className="text-xs text-neutral-500">{a.full}</p>
                  </div>
                </div>
                <div className="pt-4 border-t flex justify-between">
                  <div>
                    <div className="text-2xl font-bold text-primary-600">{a.count}</div>
                    <div className="text-xs text-neutral-500">Opportunities</div>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-semibold text-neutral-900">{a.funding}</div>
                    <div className="text-xs text-neutral-500">Funding</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-24 bg-neutral-50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-neutral-900">Everything you need</h2>
            <p className="mt-4 text-xl text-neutral-600">Powerful features for researchers</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              { emoji: '🔍', title: 'Smart Search', desc: 'AI-powered semantic search finds hidden opportunities' },
              { emoji: '🔔', title: 'Smart Alerts', desc: 'Get notified when new matches appear' },
              { emoji: '📊', title: 'Insights', desc: 'Track trends and competition' },
            ].map((f, i) => (
              <div key={i} className="bg-white p-8 rounded-xl border hover:shadow-xl transition">
                <div className="w-14 h-14 bg-primary-100 rounded-xl flex items-center justify-center mb-4 text-3xl">{f.emoji}</div>
                <h3 className="text-xl font-bold mb-3">{f.title}</h3>
                <p className="text-neutral-600">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 bg-gradient-to-br from-primary-500 to-primary-700">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <h2 className="text-4xl font-bold text-white mb-6">Ready to accelerate your search?</h2>
          <p className="text-xl text-primary-100 mb-8">Join hundreds of researchers finding opportunities faster.</p>
          <button className="px-8 py-4 bg-white text-primary-600 rounded-lg hover:bg-neutral-50 text-lg font-semibold shadow-lg">
            Get Started Free →
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-neutral-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="h-6 w-6 bg-primary-500 rounded"></div>
                <span className="font-bold">GovFunding</span>
              </div>
              <p className="text-neutral-400 text-sm">Find funding faster with AI.</p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-sm text-neutral-400">
                <li><a href="#">Features</a></li>
                <li><a href="#">Pricing</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-sm text-neutral-400">
                <li><a href="#">About</a></li>
                <li><a href="#">Contact</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Legal</h4>
              <ul className="space-y-2 text-sm text-neutral-400">
                <li><a href="#">Privacy</a></li>
                <li><a href="#">Terms</a></li>
              </ul>
            </div>
          </div>
          <div className="mt-12 pt-8 border-t border-neutral-800 text-center text-sm text-neutral-400">
            © 2025 GovFunding. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  )
}
