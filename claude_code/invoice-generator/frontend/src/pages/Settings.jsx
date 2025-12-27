import { useEffect } from 'react'
import { useMutation } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import toast from 'react-hot-toast'
import { useAuth } from '../context/AuthContext'
import { authApi } from '../api/auth'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Input from '../components/ui/Input'

const schema = z.object({
  company_name: z.string().optional(),
  address: z.string().optional(),
  phone: z.string().optional(),
  tax_id: z.string().optional(),
})

export default function Settings() {
  const { user, updateUser } = useAuth()

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(schema),
  })

  useEffect(() => {
    if (user) {
      reset({
        company_name: user.company_name || '',
        address: user.address || '',
        phone: user.phone || '',
        tax_id: user.tax_id || '',
      })
    }
  }, [user, reset])

  const updateMutation = useMutation({
    mutationFn: authApi.updateMe,
    onSuccess: (data) => {
      updateUser(data)
      toast.success('Settings updated')
    },
    onError: () => toast.error('Failed to update settings'),
  })

  const onSubmit = (data) => {
    updateMutation.mutate(data)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-500">Manage your account and business settings</p>
      </div>

      <div className="max-w-2xl">
        <Card>
          <h2 className="text-lg font-semibold mb-6">Business Information</h2>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <label className="label">Email</label>
              <input
                type="email"
                value={user?.email || ''}
                disabled
                className="input bg-gray-50 cursor-not-allowed"
              />
              <p className="mt-1 text-xs text-gray-500">Email cannot be changed</p>
            </div>

            <Input
              label="Company Name"
              {...register('company_name')}
              error={errors.company_name?.message}
              placeholder="Your company name"
            />

            <div>
              <label className="label">Address</label>
              <textarea
                {...register('address')}
                rows={3}
                className="input"
                placeholder="Your business address"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Phone"
                {...register('phone')}
                error={errors.phone?.message}
                placeholder="+1 (555) 123-4567"
              />
              <Input
                label="Tax ID / VAT Number"
                {...register('tax_id')}
                error={errors.tax_id?.message}
                placeholder="XX-XXXXXXX"
              />
            </div>

            <div className="pt-4">
              <Button type="submit" loading={updateMutation.isPending}>
                Save Changes
              </Button>
            </div>
          </form>
        </Card>

        <Card className="mt-6">
          <h2 className="text-lg font-semibold mb-4 text-red-600">Danger Zone</h2>
          <p className="text-sm text-gray-500 mb-4">
            Once you delete your account, there is no going back. Please be certain.
          </p>
          <Button
            variant="danger"
            onClick={() => {
              if (window.confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
                toast.error('Account deletion is disabled in this demo')
              }
            }}
          >
            Delete Account
          </Button>
        </Card>
      </div>
    </div>
  )
}
