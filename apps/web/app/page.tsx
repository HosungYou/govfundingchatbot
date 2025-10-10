export default function Home() {
  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white border-b border-neutral-200">
        <div className="max-w-7xl mx-auto px-6 flex items-center justify-between h-16">
          <div className="flex items-center gap-3">
            <div className="h-8 w-8 bg-primary-500 rounded-lg"></div>
            <span className="text-xl font-bold text-neutral-900">GovFunding</span>
          </div>
          <nav className="hidden md:flex gap-8">
            <a href="#features" className="text-neutral-700 hover:text-primary-600">Features</a>
            <a href="#how-it-works" className="text-neutral-700 hover:text-primary-600">How It Works</a>
          </nav>
          <div className="flex items-center gap-4">
            <button className="text-neutral-700 hover:text-primary-600">Sign In</button>
            <button className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600">
              Get Started
            </button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="bg-gradient-to-br from-primary-50 to-neutral-50 py-24">
        <div className="max-w-7xl mx-auto px-6 grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div>
            <h1 className="text-5xl lg:text-6xl font-bold text-neutral-900 leading-tight">
              Find Federal Funding{' '}
              <span className="text-primary-500">10× Faster</span>
            </h1>
            <p className="mt-6 text-xl text-neutral-600 leading-relaxed">
              AI-powered search across NSF awards and federal grants.
              Get alerts for opportunities matching your research.
            </p>
            <div className="mt-8 flex flex-col sm:flex-row gap-4">
              <button className="px-8 py-4 bg-primary-500 text-white rounded-lg hover:bg-primary-600 text-lg font-semibold">
                Try Dashboard →
              </button>
              <button className="px-8 py-4 border-2 border-primary-500 text-primary-600 rounded-lg hover:bg-primary-50 text-lg font-semibold">
                Watch Demo
              </button>
            </div>
            <div className="mt-8 flex items-center gap-2 text-sm text-neutral-500">
              <div className="flex -space-x-2">
                <div className="w-8 h-8 rounded-full bg-primary-200 border-2 border-white"></div>
                <div className="w-8 h-8 rounded-full bg-primary-300 border-2 border-white"></div>
                <div className="w-8 h-8 rounded-full bg-primary-400 border-2 border-white"></div>
              </div>
              <span>Trusted by 500+ researchers</span>
            </div>
          </div>
          <div className="hidden lg:block">
            <div className="rounded-xl shadow-2xl border border-neutral-200 bg-white p-6">
              <div className="space-y-4">
                <div className="h-12 bg-neutral-100 rounded animate-pulse"></div>
                <div className="h-64 bg-neutral-100 rounded animate-pulse"></div>
                <div className="grid grid-cols-3 gap-4">
                  <div className="h-20 bg-neutral-100 rounded animate-pulse"></div>
                  <div className="h-20 bg-neutral-100 rounded animate-pulse"></div>
                  <div className="h-20 bg-neutral-100 rounded animate-pulse"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Live Metrics Strip */}
      <section className="bg-white py-12 border-y border-neutral-200">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="text-4xl font-bold text-primary-500">1,247</div>
              <div className="mt-2 text-neutral-600">Active Opportunities</div>
              <div className="mt-1 text-sm text-green-600">↑ 34 new this week</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-primary-500">$12.4B</div>
              <div className="mt-2 text-neutral-600">Available Funding</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-primary-500">&lt;2s</div>
              <div className="mt-2 text-neutral-600">Average Search Time</div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 bg-neutral-50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-neutral-900">
              Everything you need to find funding
            </h2>
            <p className="mt-4 text-xl text-neutral-600">
              Powerful features designed for researchers and grant officers
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-white p-8 rounded-xl border border-neutral-200">
              <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
                <span className="text-2xl">🔍</span>
              </div>
              <h3 className="text-xl font-bold text-neutral-900 mb-2">Smart Search</h3>
              <p className="text-neutral-600">
                AI-powered semantic search finds opportunities you'd miss with keyword-only search.
              </p>
            </div>
            <div className="bg-white p-8 rounded-xl border border-neutral-200">
              <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
                <span className="text-2xl">🔔</span>
              </div>
              <h3 className="text-xl font-bold text-neutral-900 mb-2">Smart Alerts</h3>
              <p className="text-neutral-600">
                Get notified when new opportunities match your research areas and criteria.
              </p>
            </div>
            <div className="bg-white p-8 rounded-xl border border-neutral-200">
              <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
                <span className="text-2xl">📊</span>
              </div>
              <h3 className="text-xl font-bold text-neutral-900 mb-2">Insights</h3>
              <p className="text-neutral-600">
                Track funding trends and see which opportunities get the most attention.
              </p>
            </div>
          </div>
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
              <p className="text-neutral-400 text-sm">
                Find federal funding opportunities faster with AI.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-sm text-neutral-400">
                <li><a href="#" className="hover:text-white">Features</a></li>
                <li><a href="#" className="hover:text-white">Pricing</a></li>
                <li><a href="#" className="hover:text-white">API</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-sm text-neutral-400">
                <li><a href="#" className="hover:text-white">About</a></li>
                <li><a href="#" className="hover:text-white">Blog</a></li>
                <li><a href="#" className="hover:text-white">Contact</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Legal</h4>
              <ul className="space-y-2 text-sm text-neutral-400">
                <li><a href="#" className="hover:text-white">Privacy</a></li>
                <li><a href="#" className="hover:text-white">Terms</a></li>
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
