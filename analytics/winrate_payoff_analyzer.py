def generate_winrate_payoff_insight(win_rate, avg_win, avg_loss):
    if avg_loss == 0:
        return "Insufficient data: no recorded losing trades to calculate payoff ratio."

    payoff_ratio = round(avg_win / avg_loss, 2)
    wr_breakeven = round((avg_loss / (avg_win + avg_loss)) + 0.01, 4)
    delta = round(win_rate - wr_breakeven, 4)

    if delta >= 0.02:
        assessment = "You're comfortably above breakeven."
        advisory = "Your edge is real. Keep doing what works and focus on consistency."
    elif 0 < delta < 0.02:
        assessment = "You're just above breakeven. Margin is thin."
        advisory = "You’ve got some edge, but not much room for sloppy execution or losses that get away from you."
    elif -0.02 <= delta <= 0:
        assessment = "You're right around breakeven."
        advisory = "Any slip in discipline could push you into the red. Tighten up if possible."
    else:
        assessment = "You're running below breakeven. This math doesn't work long term."
        advisory = "Either your losses are too large or your winners too small. One of them has to improve."

    return (
        f"Your win rate is {round(win_rate * 100, 1)}%, and your average win is ${round(avg_win, 2)}, "
        f"versus an average loss of ${round(avg_loss, 2)}. That gives you a payoff ratio of {payoff_ratio}.\n"
        f"{assessment} {advisory}"
    )
