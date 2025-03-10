def parse_exchange_data(data):
    lines = data.split("\n")[2:-1]
    rates = {}
    for line in lines:
        parts = line.split("|")
        currency = parts[3].strip()
        amount = int(parts[2].strip())
        rate = float(parts[4].replace(",", ".").strip())
        rates[currency] = rate / amount
    return rates