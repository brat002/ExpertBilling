class Payment(object):
    def __init__(self):
        self.systems = []
        
        
    def register(self, obj):
        self.systems.append(obj)

class PaymentSystem(object):
    
    
    def __init__(self):
        self.slug = ''
        self.name = ''
        self.ps_type = ''
    
    def parse_response(self):
        pass
    
    def check_sign(self):
        pass
    
    def sign(self):
        pass
    
    def check(self):
        pass
    
    def pay(self):
        pass
    
class QuickPayPaymentSystem(PaymentSystem):
    
    def __init__(self):
        self.slug = 'quickpay'
        self.name = 'QuickPay'
        
p = Payment()

p.register(QuickPayPaymentSystem)
