class Exchange(object):
    def get_my_open_orders(self):
        raise NotImplementedError

    def get_my_trades(self):
        raise NotImplementedError

    def cancel_order(self, order_id):
        raise NotImplementedError
    
    def buy(self, frm, to, quantity, price):
        raise NotImplementedError

    def sell(self, frm, to, quantity, price):
        raise NotImplementedError
