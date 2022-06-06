while True:
    game_over, score = game.play_step(decision)
    if (game.ball.y + game.ball.size) >= (game.paddle_y - 6):
        if not made_decision:
            made_decision = True
            if old_state is not None:
                game_over = False
                score = game.score - score
                new_state = agent.get_state(game)
                fitness = 1
                # TODO REMOVE DEBUG TEXT
                # print('remember', (np.argmax(decision), old_state, fitness, new_state, game_over))
                agent.remember(decision, old_state, fitness, new_state, game_over)
                # print((decision, old_state, fitness, new_state, game_over))
                agent.train_short_memory(decision, old_state, fitness, new_state, game_over)

            old_state = agent.get_state(game)
            decision = agent.make_decision(old_state)

    elif made_decision:
        made_decision = False
        # game_over, score, fitness = game.play_step(decision)

    if game_over:
        if score > high_score:
            high_score = score
        print("Game:", agent.n_games, "Score:", score, "Record:", high_score)
        game.reset()
        agent.n_games += 1
        # Remember that most recent action led to loss
        game_over = True
        score = game.score - score
        new_state = agent.get_state(game)
        fitness = -10
        # TODO REMOVE DEBUG TEXT
        # print('remember', (np.argmax(decision), old_state, fitness, new_state, game_over))
        # print('reset')
        # print()
        agent.remember(decision, old_state, fitness, new_state, game_over)
        agent.train_long_memory()