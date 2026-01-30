import requests, time, csv, pandas as pd

API_KEY = "XXX"
URL = "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"

points = pd.read_csv("moje_punkty_tomtom.csv", sep=';')

while True:
    with open("wyniki_korkow.csv", 'a') as f:
        writer = csv.writer(f, delimiter=';')

        for _, row in points.iterrows():
            api_url = f"{URL}?key={API_KEY}&point={row['Współrzędne']}"
            data = requests.get(api_url).json()['flowSegmentData']

            # Obliczenie procentu korka (1 - prędkość aktualna / swobodna)
            congestion = int((1 - data['currentSpeed'] / data['freeFlowSpeed']) * 100)

            # Zapis wyniku: Ulica, Współrzędne, Godzina, Korek
            writer.writerow([row['Ulica'], row['Współrzędne'], time.strftime("%H:%M"), congestion])

    time.sleep(3600)


