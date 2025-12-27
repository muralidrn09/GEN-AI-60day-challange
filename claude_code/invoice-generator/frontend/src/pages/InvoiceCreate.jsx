import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import { useForm, useFieldArray } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { PlusIcon, TrashIcon } from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'
import { format } from 'date-fns'
import { invoicesApi } from '../api/invoices'
import { customersApi } from '../api/customers'
import { productsApi } from '../api/products'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Input from '../components/ui/Input'
import Select from '../components/ui/Select'

const itemSchema = z.object({
  product_id: z.string().optional(),
  description: z.string().min(1, 'Description is required'),
  quantity: z.coerce.number().min(0.01, 'Quantity must be greater than 0'),
  unit_price: z.coerce.number().min(0, 'Price must be 0 or greater'),
  tax_rate: z.coerce.number().min(0).max(100).optional(),
})

const schema = z.object({
  customer_id: z.coerce.number().min(1, 'Customer is required'),
  issue_date: z.string().min(1, 'Issue date is required'),
  due_date: z.string().min(1, 'Due date is required'),
  template: z.string().optional(),
  notes: z.string().optional(),
  terms: z.string().optional(),
  items: z.array(itemSchema).min(1, 'At least one item is required'),
})

export default function InvoiceCreate() {
  const navigate = useNavigate()

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
    formState: { errors },
  } = useForm({
    resolver: zodResolver(schema),
    defaultValues: {
      issue_date: format(new Date(), 'yyyy-MM-dd'),
      due_date: format(new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), 'yyyy-MM-dd'),
      template: 'classic',
      items: [{ description: '', quantity: 1, unit_price: 0, tax_rate: 0 }],
    },
  })

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'items',
  })

  const createMutation = useMutation({
    mutationFn: invoicesApi.create,
    onSuccess: () => {
      toast.success('Invoice created successfully')
      navigate('/invoices')
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to create invoice')
    },
  })

  const items = watch('items')

  const calculateSubtotal = () => {
    return items.reduce((sum, item) => sum + (item.quantity || 0) * (item.unit_price || 0), 0)
  }

  const calculateTax = () => {
    return items.reduce((sum, item) => {
      const lineTotal = (item.quantity || 0) * (item.unit_price || 0)
      return sum + lineTotal * ((item.tax_rate || 0) / 100)
    }, 0)
  }

  const calculateTotal = () => {
    return calculateSubtotal() + calculateTax()
  }

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
    createMutation.mutate({
      ...data,
      customer_id: parseInt(data.customer_id),
      items: data.items.map((item) => ({
        ...item,
        product_id: item.product_id ? parseInt(item.product_id) : null,
      })),
    })
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Create Invoice</h1>
        <p className="text-gray-500">Create a new invoice for your customer</p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <h2 className="text-lg font-semibold mb-4">Invoice Details</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Select
                  label="Customer"
                  {...register('customer_id')}
                  error={errors.customer_id?.message}
                  options={[
                    { value: '', label: 'Select a customer' },
                    ...(customers?.map((c) => ({ value: c.id, label: c.name })) || []),
                  ]}
                />
                <Select
                  label="Template"
                  {...register('template')}
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
                  error={errors.issue_date?.message}
                />
                <Input
                  label="Due Date"
                  type="date"
                  {...register('due_date')}
                  error={errors.due_date?.message}
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
                        options={[
                          { value: '', label: 'Select product (optional)' },
                          ...(products?.map((p) => ({ value: p.id, label: p.name })) || []),
                        ]}
                      />
                    </div>
                    <div className="col-span-12 md:col-span-3">
                      <Input
                        placeholder="Description"
                        {...register(`items.${index}.description`)}
                        error={errors.items?.[index]?.description?.message}
                      />
                    </div>
                    <div className="col-span-4 md:col-span-1">
                      <Input
                        type="number"
                        step="0.01"
                        placeholder="Qty"
                        {...register(`items.${index}.quantity`)}
                      />
                    </div>
                    <div className="col-span-4 md:col-span-2">
                      <Input
                        type="number"
                        step="0.01"
                        placeholder="Price"
                        {...register(`items.${index}.unit_price`)}
                      />
                    </div>
                    <div className="col-span-3 md:col-span-1">
                      <Input
                        type="number"
                        step="0.01"
                        placeholder="Tax %"
                        {...register(`items.${index}.tax_rate`)}
                      />
                    </div>
                    <div className="col-span-1">
                      {fields.length > 1 && (
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
                {errors.items?.message && (
                  <p className="text-sm text-red-600">{errors.items.message}</p>
                )}
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() =>
                    append({ description: '', quantity: 1, unit_price: 0, tax_rate: 0 })
                  }
                >
                  <PlusIcon className="h-5 w-5 mr-2" />
                  Add Item
                </Button>
              </div>
            </Card>

            <Card>
              <h2 className="text-lg font-semibold mb-4">Notes & Terms</h2>
              <div className="space-y-4">
                <div>
                  <label className="label">Notes</label>
                  <textarea
                    {...register('notes')}
                    rows={3}
                    className="input"
                    placeholder="Any additional notes for the customer..."
                  />
                </div>
                <div>
                  <label className="label">Terms & Conditions</label>
                  <textarea
                    {...register('terms')}
                    rows={3}
                    className="input"
                    placeholder="Payment terms and conditions..."
                  />
                </div>
              </div>
            </Card>
          </div>

          {/* Sidebar */}
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

            <div className="flex flex-col gap-3">
              <Button type="submit" loading={createMutation.isPending}>
                Create Invoice
              </Button>
              <Button type="button" variant="secondary" onClick={() => navigate('/invoices')}>
                Cancel
              </Button>
            </div>
          </div>
        </div>
      </form>
    </div>
  )
}
