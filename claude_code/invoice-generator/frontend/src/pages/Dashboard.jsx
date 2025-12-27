import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import {
  CurrencyDollarIcon,
  DocumentTextIcon,
  CheckCircleIcon,
  ClockIcon,
  ExclamationCircleIcon,
  UsersIcon,
} from '@heroicons/react/24/outline'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import { invoicesApi } from '../api/invoices'
import Card, { CardHeader } from '../components/ui/Card'
import Badge from '../components/ui/Badge'

function StatCard({ title, value, icon: Icon, color }) {
  const colors = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    yellow: 'bg-yellow-100 text-yellow-600',
    red: 'bg-red-100 text-red-600',
    purple: 'bg-purple-100 text-purple-600',
    gray: 'bg-gray-100 text-gray-600',
  }

  return (
    <Card>
      <div className="flex items-center">
        <div className={`p-3 rounded-xl ${colors[color]}`}>
          <Icon className="h-6 w-6" />
        </div>
        <div className="ml-4">
          <p className="text-sm font-medium text-gray-500">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
        </div>
      </div>
    </Card>
  )
}

export default function Dashboard() {
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: invoicesApi.getDashboardStats,
  })

  const { data: revenueData, isLoading: revenueLoading } = useQuery({
    queryKey: ['dashboard-revenue'],
    queryFn: () => invoicesApi.getRevenueChart(6),
  })

  const { data: recentInvoices, isLoading: recentLoading } = useQuery({
    queryKey: ['dashboard-recent'],
    queryFn: () => invoicesApi.getRecentInvoices(5),
  })

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount || 0)
  }

  if (statsLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500">Welcome back! Here's your business overview.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <StatCard
          title="Total Revenue"
          value={formatCurrency(stats?.total_revenue)}
          icon={CurrencyDollarIcon}
          color="green"
        />
        <StatCard
          title="Total Invoices"
          value={stats?.total_invoices || 0}
          icon={DocumentTextIcon}
          color="blue"
        />
        <StatCard
          title="Paid"
          value={stats?.paid_invoices || 0}
          icon={CheckCircleIcon}
          color="green"
        />
        <StatCard
          title="Pending"
          value={stats?.pending_invoices || 0}
          icon={ClockIcon}
          color="yellow"
        />
        <StatCard
          title="Overdue"
          value={stats?.overdue_invoices || 0}
          icon={ExclamationCircleIcon}
          color="red"
        />
        <StatCard
          title="Customers"
          value={stats?.total_customers || 0}
          icon={UsersIcon}
          color="purple"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Revenue Chart */}
        <Card>
          <CardHeader title="Revenue Overview" subtitle="Last 6 months" />
          <div className="h-80">
            {revenueLoading ? (
              <div className="flex items-center justify-center h-full">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={revenueData || []}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip
                    formatter={(value) => formatCurrency(value)}
                    contentStyle={{
                      backgroundColor: 'white',
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                    }}
                  />
                  <Bar dataKey="revenue" fill="#6366f1" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </Card>

        {/* Recent Invoices */}
        <Card>
          <CardHeader
            title="Recent Invoices"
            action={
              <Link to="/invoices" className="text-sm text-primary-600 hover:text-primary-500">
                View all
              </Link>
            }
          />
          <div className="space-y-4">
            {recentLoading ? (
              <div className="flex items-center justify-center h-32">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
              </div>
            ) : recentInvoices?.length > 0 ? (
              recentInvoices.map((invoice) => (
                <Link
                  key={invoice.id}
                  to={`/invoices/${invoice.id}/edit`}
                  className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div>
                    <p className="font-medium text-gray-900">{invoice.invoice_number}</p>
                    <p className="text-sm text-gray-500">{invoice.customer_name}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium text-gray-900">
                      {formatCurrency(invoice.total)}
                    </p>
                    <Badge status={invoice.status} />
                  </div>
                </Link>
              ))
            ) : (
              <p className="text-center text-gray-500 py-8">No invoices yet</p>
            )}
          </div>
        </Card>
      </div>
    </div>
  )
}
