import { useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm, useFieldArray } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { PlusIcon, TrashIcon, DocumentArrowDownIcon, EnvelopeIcon } from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'
import { invoicesApi } from '../api/invoices'
import { customersApi } from '../api/customers'
import { productsApi } from '../api/products'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Input from '../components/ui/Input'
import Select from '../components/ui/Select'
import Badge from '../components/ui/Badge'

const itemSchema = z.object({
  product_id: z.string().optional().nullable(),
  description: z.string().min(1, 'Description is required'),
  quantity: z.coerce.number().min(0.01),
  unit_price: z.coerce.number().min(0),
  tax_rate: z.coerce.number().min(0).max(100).optional(),
})

const schema = z.object({
  customer_id: z.coerce.number().min(1),
  issue_date: z.string().min(1),
  due_date: z.string().min(1),
  template: z.string().optional(),
  notes: z.string().optional(),
  terms: z.string().optional(),
  items: z.array(itemSchema).min(1),
})

export default function InvoiceEdit() {
  const { id } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const { data: invoice, isLoading } = useQuery({
    queryKey: ['invoice', id],
    queryFn: () => invoicesApi.getById(id),
  })

  const { data: customers } = useQuery({
    queryKey: ['customers'],
    queryFn: () => customersApi.getAll(),
  })

  const { data: products } = useQuery({
    queryKey: ['products'],
    queryFn: () => productsApi.getAll(),
  })

  const {
    register,
    control,
    handleSubmit,
    watch,
    setValue,
    reset,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(schema),
  })

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'items',
  })

  useEffect(() => {
    if (invoice) {
      reset({
        customer_id: invoice.customer_id,
        issue_date: invoice.issue_date,
        due_date: invoice.due_date,
        template: invoice.template,
        notes: invoice.notes || '',
        terms: invoice.terms || '',
        items: invoice.items.map((item) => ({
          product_id: item.product_id?.toString() || '',
          description: item.description,
          quantity: parseFloat(item.quantity),
          unit_price: parseFloat(item.unit_price),
          tax_rate: parseFloat(item.tax_rate || 0),
        })),
      })
    }
  }, [invoice, reset])

  const updateMutation = useMutation({
    mutationFn: (data) => invoicesApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['invoice', id])
      queryClient.invalidateQueries(['invoices'])
      toast.success('Invoice updated')
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to update')
    },
  })

  const statusMutation = useMutation({
    mutationFn: (status) => invoicesApi.updateStatus(id, status),
    onSuccess: () => {
      queryClient.invalidateQueries(['invoice', id])
      queryClient.invalidateQueries(['invoices'])
      toast.success('Status updated')
    },
    onError: () => toast.error('Failed to update status'),
  })

  const emailMutation = useMutation({
    mutationFn: () => invoicesApi.sendEmail(id),
    onSuccess: () => toast.success('Invoice sent'),
    onError: (error) => toast.error(error.response?.data?.detail || 'Failed to send'),
  })

  const handleDownloadPdf = async () => {
    try {
      const blob = await invoicesApi.downloadPdf(id)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `invoice_${invoice?.invoice_number}.pdf`
      a.click()
      window.URL.revokeObjectURL(url)
    } catch {
      toast.error('Failed to download PDF')
    }
  }

  const items = watch('items') || []

  const calculateSubtotal = () => {
    return items.reduce((sum, item) => sum + (item.quantity || 0) * (item.unit_price || 0), 0)
  }

  const calculateTax = () => {
    return items.reduce((sum, item) => {
      const lineTotal = (item.quantity || 0) * (item.unit_price || 0)
      return sum + lineTotal * ((item.tax_rate || 0) / 100)
    }, 0)
  }

  const calculateTotal = () => calculateSubtotal() + calculateTax()

  const handleProductSelect = (index, productId) => {
    if (productId) {
      const product = products?.find((p) => p.id === parseInt(productId))
      if (product) {
        setValue(`items.${index}.description`, product.name)
        setValue(`items.${index}.unit_price`, parseFloat(product.unit_price))
        setValue(`items.${index}.tax_rate`, parseFloat(product.tax_rate || 0))
      }
    }
  }

  const onSubmit = (data) => {
    updateMutation.mutate({
      ...data,
      customer_id: parseInt(data.customer_id),
      items: data.items.map((item) => ({
        ...item,
        product_id: item.product_id ? parseInt(item.product_id) : null,
      })),
    })
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  const isPaid = invoice?.status === 'paid'

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Invoice {invoice?.invoice_number}
          </h1>
          <div className="flex items-center gap-2 mt-1">
            <Badge status={invoice?.status} />
          </div>
        </div>
        <div className="flex gap-3">
          <Button variant="secondary" onClick={handleDownloadPdf}>
            <DocumentArrowDownIcon className="h-5 w-5 mr-2" />
            Download PDF
          </Button>
          <Button variant="secondary" onClick={() => emailMutation.mutate()} loading={emailMutation.isPending}>
            <EnvelopeIcon className="h-5 w-5 mr-2" />
            Send Email
          </Button>
        </div>
      </div>

      {/* Status Actions */}
      <Card>
        <div className="flex items-center gap-3">
          <span className="text-sm font-medium text-gray-500">Mark as:</span>
          {['draft', 'sent', 'paid', 'overdue', 'cancelled'].map((status) => (
            <button
              key={status}
              onClick={() => statusMutation.mutate(status)}
              disabled={invoice?.status === status || statusMutation.isPending}
              className={`px-3 py-1.5 text-sm font-medium rounded-lg transition-colors capitalize ${
                invoice?.status === status
                  ? 'bg-primary-100 text-primary-700'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200 disabled:opacity-50'
              }`}
            >
              {status}
            </button>
          ))}
        </div>
      </Card>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <h2 className="text-lg font-semibold mb-4">Invoice Details</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Select
                  label="Customer"
                  {...register('customer_id')}
                  error={errors.customer_id?.message}
                  disabled={isPaid}
                  options={[
                    { value: '', label: 'Select a customer' },
                    ...(customers?.map((c) => ({ value: c.id, label: c.name })) || []),
                  ]}
                />
                <Select
                  label="Template"
                  {...register('template')}
                  disabled={isPaid}
                  options={[
                    { value: 'classic', label: 'Classic' },
                    { value: 'modern', label: 'Modern' },
                    { value: 'minimal', label: 'Minimal' },
                  ]}
                />
                <Input
                  label="Issue Date"
                  type="date"
                  {...register('issue_date')}
                  disabled={isPaid}
                />
                <Input
                  label="Due Date"
                  type="date"
                  {...register('due_date')}
                  disabled={isPaid}
                />
              </div>
            </Card>

            <Card>
              <h2 className="text-lg font-semibold mb-4">Line Items</h2>
              <div className="space-y-4">
                {fields.map((field, index) => (
                  <div key={field.id} className="grid grid-cols-12 gap-3 items-start">
                    <div className="col-span-12 md:col-span-4">
                      <Select
                        {...register(`items.${index}.product_id`)}
                        onChange={(e) => handleProductSelect(index, e.target.value)}
                        disabled={isPaid}
                        options={[
                          { value: '', label: 'Select product' },
                          ...(products?.map((p) => ({ value: p.id, label: p.name })) || []),
                        ]}
                      />
                    </div>
                    <div className="col-span-12 md:col-span-3">
                      <Input
                        placeholder="Description"
                        {...register(`items.${index}.description`)}
                        disabled={isPaid}
                      />
                    </div>
                    <div className="col-span-4 md:col-span-1">
                      <Input
                        type="number"
                        step="0.01"
                        {...register(`items.${index}.quantity`)}
                        disabled={isPaid}
                      />
                    </div>
                    <div className="col-span-4 md:col-span-2">
                      <Input
                        type="number"
                        step="0.01"
                        {...register(`items.${index}.unit_price`)}
                        disabled={isPaid}
                      />
                    </div>
                    <div className="col-span-3 md:col-span-1">
                      <Input
                        type="number"
                        step="0.01"
                        {...register(`items.${index}.tax_rate`)}
                        disabled={isPaid}
                      />
                    </div>
                    <div className="col-span-1">
                      {!isPaid && fields.length > 1 && (
                        <button
                          type="button"
                          onClick={() => remove(index)}
                          className="p-2 text-red-500 hover:bg-red-50 rounded"
                        >
                          <TrashIcon className="h-5 w-5" />
                        </button>
                      )}
                    </div>
                  </div>
                ))}
                {!isPaid && (
                  <Button
                    type="button"
                    variant="secondary"
                    onClick={() => append({ description: '', quantity: 1, unit_price: 0, tax_rate: 0 })}
                  >
                    <PlusIcon className="h-5 w-5 mr-2" />
                    Add Item
                  </Button>
                )}
              </div>
            </Card>

            <Card>
              <h2 className="text-lg font-semibold mb-4">Notes & Terms</h2>
              <div className="space-y-4">
                <div>
                  <label className="label">Notes</label>
                  <textarea {...register('notes')} rows={3} className="input" disabled={isPaid} />
                </div>
                <div>
                  <label className="label">Terms</label>
                  <textarea {...register('terms')} rows={3} className="input" disabled={isPaid} />
                </div>
              </div>
            </Card>
          </div>

          <div className="space-y-6">
            <Card>
              <h2 className="text-lg font-semibold mb-4">Summary</h2>
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Subtotal</span>
                  <span className="font-medium">{formatCurrency(calculateSubtotal())}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Tax</span>
                  <span className="font-medium">{formatCurrency(calculateTax())}</span>
                </div>
                <div className="border-t pt-3 flex justify-between">
                  <span className="font-semibold">Total</span>
                  <span className="text-xl font-bold text-primary-600">
                    {formatCurrency(calculateTotal())}
                  </span>
                </div>
              </div>
            </Card>

            {!isPaid && (
              <div className="flex flex-col gap-3">
                <Button type="submit" loading={updateMutation.isPending}>
                  Save Changes
                </Button>
                <Button type="button" variant="secondary" onClick={() => navigate('/invoices')}>
                  Cancel
                </Button>
              </div>
            )}
          </div>
        </div>
      </form>
    </div>
  )
}
