---
name: parts-and-inventory
description: Parts, stock and suppliers — check what is on hand and where, move stock between locations, look up a price, and raise a purchase order. Use for "do we have this part", "how much stock at the van", "transfer parts to the warehouse", "what do we charge for X", "raise a PO".
---

# Parts, stock and suppliers

## Check stock

```
get_inventory({ filters: [], limit: 20 })     // filters is required
get_inventory_by_id({ ... })                  // one stock row
get_warehouses()                              // locations, incl. technician vans
```

Stock lives per **location**, so "do we have it" is always "where". Report the location
name alongside the quantity — a part sitting in another van is not available to today's
job.

## Prices and the catalogue

```
get_products_services({ filters: [], limit: 20 })
get_product_service_by_id({ ... })
get_product_categories()
get_units_of_measurement()
```

Quote the stored `price`. If the user asks "what do we charge", read it — do not estimate.

## Move stock

`transfer_inventory` moves quantity between locations. It **decrements the source**, so
it is a destructive write: confirm the part, the quantity and both locations before
calling it, and never round a quantity the user gave you.

## Add a product or service

All fields go inside `product_service_data`. Required: `name`, `type`
(`"Product"` or `"Service"`), `price`.

```
create_product_service({ product_service_data: {
  name: "AC Service Call", type: "Service", price: 150, duration: 60
}})
```

### If you turn on stock tracking

Setting `isInventoried: true` makes the `inventory` block **required**, and it has two
traps:

```
inventory: {
  locationId: "<24-hex warehouse ObjectId>",   // REQUIRED — get it from get_warehouses.
                                               // The key is locationId, NOT warehouseId,
                                               // warehouse or location.
  sku: "SKU-001",                              // REQUIRED and globally unique
  quantity: 10,
  lowStockAlert: 5
}
```

A missing `locationId` or `sku`, or a duplicate `sku`, is what makes this call fail. If
the user does not need stock tracking, leave `isInventoried` off and skip the block
entirely — that is the simpler, safer path.

## Suppliers and purchase orders

```
get_vendors({ filters: [], limit: 20 })
get_purchase_orders({ filters: [], limit: 10 })
create_purchase_order({ ... })                 // additive
```

`get_purchase_orders` returns a large payload — keep `limit` small.

## Deletes

`delete_product_service`, `delete_inventory`, `delete_warehouse`, `delete_vendor`,
`delete_purchase_order` all remove records from the user's active data. Confirm the exact
record by name and id before calling any of them, and never delete "the old ones" on a
vague instruction — ask which.
