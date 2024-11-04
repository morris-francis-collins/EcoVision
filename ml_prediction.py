import torch
import torch.nn as nn
import math

class NN(nn.Module):
    def __init__(self):
        super().__init__()
        self.convs = nn.Sequential(
            nn.Linear(9, 128),
            nn.LeakyReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.LeakyReLU(),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 7),
        )
    def forward(self, x):
        return self.convs(x)

    def predict(self, x):
        self.eval()
        with torch.no_grad():
            return self.forward(x)


model = NN()
model.load_state_dict(torch.load('new_model2.pth'))
model.eval()

num_to_county = {0: 'Alameda', 1: 'Alpine', 2: 'Amador', 3: 'Butte', 4: 'Calaveras', 5: 'Colusa', 6: 'Contra Costa', 7: 'Del Norte', 8: 'El Dorado', 9: 'Fresno', 10: 'Glenn', 11: 'Humboldt', 12: 'Imperial', 13: 'Inyo', 14: 'Kern', 15: 'Kings', 16: 'Lake', 17: 'Lassen', 18: 'Los Angeles', 19: 'Madera', 20: 'Marin', 21: 'Mariposa', 22: 'Mendocino', 23: 'Merced', 24: 'Modoc', 25: 'Mono', 26: 'Monterey', 27: 'Napa', 28: 'Nevada', 29: 'Orange', 30: 'Placer', 31: 'Plumas', 32: 'Riverside', 33: 'Sacramento', 34: 'San Benito', 35: 'San Bernardino', 36: 'San Diego', 37: 'San Francisco', 38: 'San Joaquin', 39: 'San Luis Obispo', 40: 'San Mateo', 41: 'Santa Barbara', 42: 'Santa Clara', 43: 'Santa Cruz', 44: 'Shasta', 45: 'Sierra', 46: 'Siskiyou', 47: 'Solano', 48: 'Sonoma', 49: 'Stanislaus', 50: 'Sutter', 51: 'Tehama', 52: 'Trinity', 53: 'Tulare', 54: 'Tuolumne', 55: 'Ventura', 56: 'Yolo', 57: 'Yuba'}
county_to_num = {'Alameda': 0, 'Alpine': 1, 'Amador': 2, 'Butte': 3, 'Calaveras': 4, 'Colusa': 5, 'Contra Costa': 6, 'Del Norte': 7, 'El Dorado': 8, 'Fresno': 9, 'Glenn': 10, 'Humboldt': 11, 'Imperial': 12, 'Inyo': 13, 'Kern': 14, 'Kings': 15, 'Lake': 16, 'Lassen': 17, 'Los Angeles': 18, 'Madera': 19, 'Marin': 20, 'Mariposa': 21, 'Mendocino': 22, 'Merced': 23, 'Modoc': 24, 'Mono': 25, 'Monterey': 26, 'Napa': 27, 'Nevada': 28, 'Orange': 29, 'Placer': 30, 'Plumas': 31, 'Riverside': 32, 'Sacramento': 33, 'San Benito': 34, 'San Bernardino': 35, 'San Diego': 36, 'San Francisco': 37, 'San Joaquin': 38, 'San Luis Obispo': 39, 'San Mateo': 40, 'Santa Barbara': 41, 'Santa Clara': 42, 'Santa Cruz': 43, 'Shasta': 44, 'Sierra': 45, 'Siskiyou': 46, 'Solano': 47, 'Sonoma': 48, 'Stanislaus': 49, 'Sutter': 50, 'Tehama': 51, 'Trinity': 52, 'Tulare': 53, 'Tuolumne': 54, 'Ventura': 55, 'Yolo': 56, 'Yuba': 57}

race_to_percent = {"white": [0.6, 0.1, 0.2, 0.1], "hispanic": [0.2, 0.2, 0.1, 0.5], "black": [0.2, 0.6, 0.1, 0.1], "asian": [0.3, 0.1, 0.5, 0.1], "native-american": [0.4, 0.3, 0.1, 0.2], "pacific islander": [0.2, 0.2, 0.5, 0.1], "other": [0.25, 0.25, 0.25, 0.25], "prefer-not-to-say": [0.25, 0.25, 0.25, 0.25]}
employment_to_percentile = {"Employed": 75, "Unemployed": 25}
education_to_percentile = {"No high-school": 15, "high-school": 30, "bachelor-degree": 65, "graduate-degree": 90, "other": 50}

def predict(county_name, race, income, employment_status, education, age):
    county = county_to_num[county_name]
    white, black, asian, hispanic = race_to_percent[race]
    income = 1 / (1 + math.exp((85000 - age) / 30000))
    unemployment = employment_to_percentile[employment_status] 
    education = education_to_percentile[education]
    age = 1 / (1 + math.exp((65 - age) / 10))

    input_tensor = torch.tensor([white, black, asian, hispanic, county, age, income, unemployment, age])

    model.eval()
    with torch.no_grad():
        predictions = model(input_tensor)

    return predictions.tolist()

# returns array of length 7
# array[0] = percentile low life expectancy
# array[1] = percentile expected building loss rate in next 30 years
# array[2] = percentile share of properties at risk of flood in 30 years
# array[3] = percentile share of properties at risk of fire in 30 years
# array[4] = percentile traffic proximity and volume
# array[5] = percentile bad air quality
# array[6] = percentile bad water quality