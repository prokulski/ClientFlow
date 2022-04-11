from events.events_routings import customer_buys_product, new_customer, new_product

event_types = {"new_customer": new_customer, "new_product": new_product, "customer_buys_product": customer_buys_product}
