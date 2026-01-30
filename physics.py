import numpy as np
import config

CELL_SIZE_M = 100.0  # 1 piksel mapy to kwadrat 100x100 metrów w rzeczywistości.
TIME_STEP_S = 300.0  # 1 klatka symulacji to upływ 5 minut (300 sekund).


def safe_shift(arr, sx, sy):
    result = np.roll(arr, (sy, sx), axis=(0, 1))
    if sy > 0:
        result[:sy, :] = 0
    elif sy < 0:
        result[sy:, :] = 0
    if sx > 0:
        result[:, :sx] = 0
    elif sx < 0:
        result[:, sx:] = 0
    return result


def update_simulation_step(current_smog, base_source, gios_pm10,
                           diffusion_rate, decay_rate, wind_params,
                           congestion_map, traffic_volume):

    # road_mask to mapa przepuszczalności (1.0 = autostrada, 0.0 = trawnik).
    road_mask = np.clip(base_source / 25.0, 0, 1)

    # tło miejskie 30% emisji
    background_emission = gios_pm10 * road_mask * config.RATIO_BACKGROUND

    # Iloczyn czynników (Korek * Ilość Aut * Skalar)
    # aby program nie oszukiwał, oznaczając wązką ulicę w nocy na której jest jedno auto, jako korek
    traffic_intensity = (congestion_map * traffic_volume * config.TRAFFIC_EMISSION_SCALAR)

    # Nałożenie na maskę drogową i zastosowanie wagi 70%
    traffic_emission = traffic_intensity * road_mask * config.RATIO_TRAFFIC

    # suma
    total_new_emission = background_emission + traffic_emission

    current_smog += total_new_emission

    # dyfuzja
    up = np.roll(current_smog, -1, axis=0)
    down = np.roll(current_smog, 1, axis=0)
    left = np.roll(current_smog, -1, axis=1)
    right = np.roll(current_smog, 1, axis=1)
    current_smog += diffusion_rate * ((up + down + left + right) - 4 * current_smog)


    # wiatr
    if wind_params['speed'] > 0.01:
        sx, sy = int(wind_params['dir_x']), int(wind_params['dir_y'])

        # Fizyka: S = V * t
        wind_ms = (wind_params['speed'] * 50.0) / 3.6
        shift_cells = (wind_ms * TIME_STEP_S) / CELL_SIZE_M

        # Interpolacja liniowa (Wygładzanie ruchu)
        factor = min(shift_cells, 1.0)
        shifted = safe_shift(current_smog, sx, sy)
        current_smog = current_smog * (1 - factor) + shifted * factor


    # rozpad - co krok traci 1% / okolo 8h do calego rozpadu
    current_smog *= (1 - decay_rate)

    # zerowanie krawędzi mapy
    current_smog[0, :] = current_smog[-1, :] = current_smog[:, 0] = current_smog[:, -1] = 0

    return current_smog