domino_spacing = 0.5  # Spacing between dominoes
start_x = 5  # Starting x position on the platform
bowling_ball_radius = 0.5  # 0.5 meters radius
small_gap = 0.1  # Gap between last domino and bowling ball


def gen_simple(
    ratios=[3, 6, 9, 12], num_dominoes=[5, 10, 20], skip=[0, 2, 4], domino_width=0.2
):
    scenario = []

    for ratio in ratios:
        domino_height = domino_width * ratio
        for n_dominoes in num_dominoes:
            for n_skip in skip:
                scenario.append(f"width({domino_width}).")
                scenario.append(f"height({domino_height}).")

                mid = n_dominoes // 2
                skip_start = mid - n_skip // 2
                skip_end = mid + n_skip // 2
                pushed = False
                for i in range(n_dominoes):
                    if skip_start <= i < skip_end:
                        continue

                    domino_x = start_x + i * (domino_width + domino_spacing)
                    if not pushed:
                        scenario.append(f"push(domino({domino_x})).")
                        pushed = True

                    scenario.append(f"domino({domino_x}).")

                last_domino_x = start_x + (n_dominoes - 1) * (
                    domino_width + domino_spacing
                )
                bowling_ball_x = (
                    last_domino_x + domino_width / 2 + bowling_ball_radius + small_gap
                )
                scenario.append(f"ball_x({bowling_ball_x}).")

                yield scenario
                scenario.clear()


if __name__ == "__main__":
    for i, s in enumerate(gen_simple()):
        with open(f"scenarios/simple_{i}.pl", "w") as f:
            f.write("\n".join(s))
