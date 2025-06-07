from strategies.base import Strategy

class ThreeEMACrossover(Strategy, name="three_ema_crossover"):
    def execute(self, df, owned_stocks, price, capital):
        crossover_now = df['indicator_three_ema_crossover'].iloc[-1]

        if crossover_now > 1:
            max_buy = capital // price
            buy_number = max_buy / 10 * crossover_now
            return buy_number, [price * 0.93, buy_number], [price * 1.05, buy_number]

        if crossover_now < -1:
            sell_number = owned_stocks / 5 * crossover_now
            return sell_number, False, False

        return 0, False, False
