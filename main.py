from abc import ABC, abstractmethod

class StockExchange:
    def __init__(self):
        self.buy_order = []
        self.sell_order = []
        self.orders = {}
        self.last_prices = {}
        
    def place_order(self, order):
        number = len(self.orders) + 1
        self.orders[number] = order
        order.message()
        self.matching(order)
        return self.orders

    def matching(self, order):
        if order._action == "BUY":
            self.buy_order.append(order)

        if order._action == "SELL":
            self.sell_order.append(order)

        for buy in self.buy_order:
            for sell in self.sell_order:
                if buy._name == sell._name:
                    is_market_deal = (buy._type == "MKT" or sell._type == "MKT")
                    is_limit_deal = (buy._type == "LMT" and sell._type == "LMT" and buy._price >= sell._price)

                    if is_market_deal or is_limit_deal:
                        buy_left = buy._shares - buy._filled_shares
                        sell_left = sell._shares - sell._filled_shares

                        traded_shares = min(buy_left, sell_left)

                        if traded_shares > 0:
                            buy._filled_shares += traded_shares
                            sell._filled_shares += traded_shares

                            deal_price = None
                            if buy._type == "LMT":
                                deal_price = buy._price
                            elif sell._type == "LMT":
                                deal_price = sell._price

                            if deal_price is not None:
                                self.last_prices[buy._name] = deal_price

                            buy.order_status()
                            sell.order_status()


    def view_orders(self):
        for number, order in self.orders.items():
            print(f"{number}. {order}")
        print()

    def quote_order(self, ticker):
        ticker_sell = [order for order in self.sell_order if order._name == ticker and order._type == "LMT" and order._status != "FILLED"]
        ticker_buy = [order for order in self.buy_order if order._name == ticker and order._type == "LMT" and order._status != "FILLED"]

        if ticker_buy:
            bid = max(ticker_buy, key=lambda x: x._price)._price
            bid_str = f"${bid:.2f}"
        else:
            bid_str = "None"

        if ticker_sell:
            ask = min(ticker_sell, key=lambda x: x._price)._price
            ask_str = f"${ask:.2f}"
        else:
            ask_str = "None"

        last = self.last_prices.get(ticker, None)
        last_str = f"${last:.2f}" if last is not None else "None"

        print(f"{ticker} BID: {bid_str} ASK: {ask_str} LAST: {last_str}")
        print()
            


class Order(ABC):
    def __init__(self, action, name, type, shares):
        self._action = action
        self._name = name
        self._shares = int(shares)
        self._type = type

        if self._shares <= 0:
            raise ValueError("Количество акций не может быть нулевым или отрицательным!")
        
        self._filled_shares = 0
        self._status = "PENDING"
    
    @abstractmethod
    def order_status(self):
        pass

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def message(self):
        pass


class LimitOrder(Order):
    def __init__(self, action, name, type, price, shares):
        super().__init__(action, name, type, shares)
        new_price = float(price.replace('$', ''))
        if new_price <= 0:
            raise ValueError("Цена не может быть нулевой или отрицательной!")
        self._price = new_price


    def order_status(self):
        
        if self._filled_shares == 0:
            self._status = "PENDING"

        if 0 < self._filled_shares < self._shares:
            self._status = "PARTIAL"
        
        if self._filled_shares == self._shares:
            self._status = "FILLED"

        return f"{self._filled_shares}/{self._shares} {self._status}"


    def message(self):
        print(f"You have placed a limit {str(self._action).lower()} order for {self._shares} {self._name} shares at ${self._price:.2f} each.")
        print()
    

    def __str__(self):
        return f"{self._name} {self._type} {self._action} ${self._price:.2f} {self._filled_shares}/{self._shares} {self._status}"


class MarketOrder(Order):
    def __init__(self, action, name, type, shares):
        super().__init__(action, name, type, shares)

    def order_status(self):
        
        if self._filled_shares == 0:
            self._status = "PENDING"

        if 0 < self._filled_shares < self._shares:
            self._status = "PARTIAL"
        
        if self._filled_shares == self._shares:
            self._status = "FILLED"

        return f"{self._filled_shares}/{self._shares} {self._status}"

    def message(self):
        print(f"You have placed a market order for {self._shares} {self._name} shares.")
        print()

    def quote_order(self):
        pass

    def __str__(self):
        return f"{self._name} {self._type} {self._action} {self._filled_shares}/{self._shares} {self._status}"



if __name__ == "__main__":
    exchange = StockExchange()

    while True:
        try:
            action = input("ACTION: ")

            if action == "QUIT":
                print ("No output")
                break

            elif action == "VIEW ORDERS":
                exchange.view_orders()

            elif "QUOTE" in action:
                parts = action.split()
                if len(parts) < 2:
                    print("Укажите тикер!")
                    print()
                name = parts[1]
                exchange.quote_order(name)  
               
            else:
                user_order = action
                user_order_split = user_order.split()
                if "LMT" in user_order_split:
                    new_order = LimitOrder(*user_order_split)
                elif "MKT" in user_order_split:
                    new_order = MarketOrder(*user_order_split)
                else:
                    print("Неизвестная команда.")
                    print()
                    continue

                exchange.place_order(new_order) 

        except(ValueError) as e:
            print(f"Ошибка! {e}")
            print()

        except(TypeError, IndexError):
            print("Ошибка! Проверьте правильность написания команды.")
            print()