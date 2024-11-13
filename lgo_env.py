class LGOEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, dataframe, num_gates=100000, alpha=1, beta=1, gamma=1):
        super(LGOEnv, self).__init__()
        self.df = dataframe.copy().reset_index(drop=True)
        self.num_gates = min(num_gates, len(self.df))
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma

        self.action_space = spaces.Discrete(3)  # 0: Change cell, 1: Resize gate, 2: Reroute net
        self.observation_space = spaces.Box(
            low=self.df.min().min(),
            high=self.df.max().max(),
            shape=(self.df.shape[1],),
            dtype=np.float32
        )

        self.current_step = 0
        self.reset() 


    def reset(self):
        self.current_step = 0
        self.current_power = self._calculate_power()
        self.current_delay = self._calculate_delay()
        self.current_area = self._calculate_area()
        self.episode_rewards = []
        return self.df.iloc[0].values.astype(np.float32)


    def step(self, action):
        self._apply_action(action)
        reward = self._calculate_reward()
        self.episode_rewards.append(reward)

        self.current_step += 1
        done = self.current_step >= self.num_gates
        next_obs = self.df.iloc[self.current_step % len(self.df)].values.astype(np.float32) if not done else self.reset()
        return next_obs, reward, done, {}



    def _calculate_reward(self):
        new_power = self._calculate_power()
        new_delay = self._calculate_delay()
        new_area = self._calculate_area()

        power_reduction = self.current_power - new_power
        delay_reduction = self.current_delay - new_delay
        area_increase = new_area - self.current_area

        self.current_power = new_power
        self.current_delay = new_delay
        self.current_area = new_area

        reward = -self.alpha * power_reduction + self.beta * delay_reduction - self.gamma * area_increase
        return reward


    def _apply_action(self, action):
        current_row_index = self.current_step % len(self.df)

        if action == 0:  # Change cell type
            available_cell_types = self.df['libcell_name'].unique().tolist()
            current_cell_type = self.df.loc[current_row_index, 'libcell_name']
            new_cell_type = random.choice([ct for ct in available_cell_types if ct != current_cell_type])
            self.df.loc[current_row_index, 'libcell_name'] = new_cell_type
            self._update_cell_parameters(current_row_index) 

        elif action == 1:(adjust input pin capacitance)
            current_cap = self.df.loc[current_row_index, 'input_pin_cap']
            scaling_factor = random.uniform(0.8, 1.2)
            new_cap = current_cap * scaling_factor
            self.df.loc[current_row_index, 'input_pin_cap'] = new_cap
            self._update_cell_parameters(current_row_index)

        elif action == 2:  # Reroute net
            current_net = self.df.loc[current_row_index, 'net_name']
            alternative_nets = self._get_alternative_nets(current_net)
            if alternative_nets:
                new_net = random.choice(alternative_nets)
                self.df.loc[current_row_index, 'net_name'] = new_net

                affected_cells = self.df[self.df['net_name'].isin([current_net, new_net])].index.tolist()
                for cell_index in affected_cells:
                self._update_cell_parameters(cell_index)


    def _get_alternative_nets(self, current_net):
        cell_nets = self.df[self.df['cell_name'] == self.df.loc[self.current_step % len(self.df), 'cell_name']]['net_name'].unique().tolist()
        return [net for net in cell_nets if net != current_net]

    def _update_cell_parameters(self, row_index):
        
        libcell_name = self.df.loc[row_index, 'libcell_name']
        input_pin_cap = self.df.loc[row_index, 'input_pin_cap']
        net_name = self.df.loc[row_index, 'net_name']


       # Linear coefficient
        static_power_coeff = 0.1  
        dynamic_power_coeff = 0.05
        delay_coeff = 0.01
        area_coeff = 0.02

        self.df.loc[row_index, 'cell_static_power'] = static_power_coeff * len(libcell_name)
        self.df.loc[row_index, 'cell_dynamic_power'] = dynamic_power_coeff * input_pin_cap 

        self.df.loc[row_index, 'fo4_delay'] = delay_coeff * len(libcell_name) * input_pin_cap



        self.df.loc[row_index, 'x'] *=  area_coeff * len(libcell_name)
        self.df.loc[row_index, 'y'] *= area_coeff * len(libcell_name)


    def _calculate_power(self):
        return (self.df['cell_static_power'] + self.df['cell_dynamic_power']).sum()

    def _calculate_delay(self):
        return self.df['fo4_delay'].max()

    def _calculate_area(self):
        return (self.df['x'] * self.df['y']).sum()
