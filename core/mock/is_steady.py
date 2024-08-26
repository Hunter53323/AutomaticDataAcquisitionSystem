def arrive():
    history_n = []
    def is_steady(target_n,curr_n, epsilon_n=1, epsilon_a=1):
        if not history_n:
            history_n.append(curr_n)
            return False
        if abs(curr_n - history_n[-1]) < epsilon_a and abs(curr_n - target_n) < epsilon_n:
            return True
        else:
            history_n.append(curr_n)
            return False
    return is_steady

if __name__ == "__main__":
    target_n = 23.8
    check_steady_state = arrive()
    test_rotations = [0, 5, 10, 20, 30, 25, 23, 24, 23.5, 23.5]
    for rotation in test_rotations:
        print(check_steady_state(target_n,rotation))

