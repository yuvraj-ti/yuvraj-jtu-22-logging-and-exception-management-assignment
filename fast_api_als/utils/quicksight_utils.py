import time


def create_quicksight_data(obj, lead_hash, status, code):
    item = {
        "lead_hash": lead_hash,
        "status": status,
        "epoch_timestamp": int(time.time()),
        "code": code,
        "make": obj.get('vehicle', {}).get('make', 'unknown'),
        "model": obj.get('vehicle', {}).get('model', 'unknown'),
        "conversion": 0,
        "postalcode": obj.get('customer', {}).get('contact', {}).get('address', {}).get('postalcode', 'unknown'),
        "email_provided": 1 if obj.get('customer', {}).get('contact', {}).get('email', None) else 0,
        "phone_provided": 1 if obj.get('customer', {}).get('contact', {}).get('phone', None) else 0,
        "3pl": obj.get('provider', {}).get('service', 'unknown'),
        "dealer": obj.get('vendor', {}).get('id', {}).get('#text', 'unknown')+"_"+obj.get('vendor', {}).get('vendorname', 'unknown')
    }
    return item, f"{obj.get('vehicle', {}).get('make', 'unknown')}/{item['epoch_timestamp']}_0_{lead_hash}"