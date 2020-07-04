import numpy as np
import json

class Otomat:
    def __init__(self, sigma, S, S0, F, delta):
        self.sigma = sigma
        self.S = S
        self.S0 = S0 
        self.F = F 
        self.delta = delta
        self.extraState = 'ES'      #đỉnh thêm mới (nếu có)

    '''
        Đầy đủ hóa otomat đơn định - điền hàm chuyển trạng thái rỗng
    '''
    def fill_otomat(self):
        for state in self.S:
            if state not in self.delta.keys():
                self.delta[state] = {}

            for symbol in self.sigma:
                if symbol not in self.delta[state].keys():
                    self.delta[state][symbol] = [self.extraState]
                    if self.extraState not in self.S:
                        self.S.append(self.extraState)

                elif len(self.delta[state][symbol]) == 0:
                    self.delta[state][symbol] = [self.extraState]
                    if self.extraState not in self.S:
                        self.S.append(self.extraState)

    def mark_table(self):
        table = np.zeros((len(self.S), len(self.S)), dtype = np.bool)
        while 1:
            unmarkable = True
            for i in range(len(self.S)):
                firstState = self.S[i]
                for j in range(len(self.S)):
                    secondState = self.S[j]
                    if table[i][j]:
                        continue
                    if firstState in self.F and secondState not in self.F:
                        unmarkable = False
                        table[i][j] = 1
                    else:
                        for symbol in self.sigma:
                            temp_firstState = self.delta[firstState][symbol][0]
                            temp_secondState = self.delta[secondState][symbol][0]
                            if table[self.S.index(temp_firstState)][self.S.index(temp_secondState)] or table[self.S.index(temp_secondState)][self.S.index(temp_firstState)]:
                                unmarkable = False
                                table[i][j] = 1
                                break
            if unmarkable:
                break
        return table

    def combine_unmarked(self, table):
        unmarked_states_group = []
        for i in range(len(self.S)):
            for j in range(len(self.S)):
                if i == j:
                    continue
                if table[i][j] == 0:
                    if [self.S[i], self.S[j]] not in unmarked_states_group and [self.S[j], self.S[i]] not in unmarked_states_group:
                        # [C, D], [D, E], [E, C] -> [C, D, E]
                        check = False
                        for k in range(len(unmarked_states_group)):
                            if self.S[i] in unmarked_states_group[k] or self.S[j] in unmarked_states_group[k]:
                                check = True
                                unmarked_states_group[k] += [self.S[i], self.S[j]]
                                unmarked_states_group[k] = list(set(unmarked_states_group[k]))
                                break
                        if not check:
                            unmarked_states_group.append([self.S[i], self.S[j]])
        return unmarked_states_group
    
    def minimize(self):

        self.fill_otomat()
        table = self.mark_table()
        unmarked_states_group = self.combine_unmarked(table)

        # Xây dựng otomat mới
        for group in unmarked_states_group:
            # Tạo trạng thái mới và thay thế trạng thái cũ
            new_state = '_'.join(group)
            self.S.append(new_state)
            self.delta[new_state] = {}
            for state in group:
                self.S.remove(state)
                for symbol in self.sigma:
                    if symbol not in self.delta[new_state]:
                        self.delta[new_state][symbol] = []
                    self.delta[new_state][symbol] += self.delta[state][symbol]
                del self.delta[state]

        # Thay thế trạng thái cũ trong bảng chuyển trạng thái
        for state in self.S:
            for symbol in self.sigma:
                for idx, trans_state in enumerate(self.delta[state][symbol]):
                    if trans_state not in self.S:
                        for new_state in self.S:
                            if trans_state in new_state:
                                self.delta[state][symbol][idx] = new_state
                self.delta[state][symbol] = list(set(self.delta[state][symbol]))    

        # Thay thế trạng thái cũ trong tập trạng thái kết
        for idx, final_state in enumerate(self.F):
            if final_state not in self.S:
                for state in self.S:
                    if final_state in state:
                        self.F[idx] = state
        self.F = list(set(self.F))

def input_otomat(self):
    with open("test.json", "r") as json_file:
        data = json.load(json_file)

    sigma = []
    S = []
    S0 = []
    F = []
    delta = []

    assert data["S"], "Lỗi: không tìm thấy tập trạng thái"
    assert data["sigma"], "Lỗi: không tìm thấy bảng chữ cái"
    assert data["S0"], "Lỗi: không tìm thấy tập trạng thái bắt đầu"
    assert data["F"], "Lỗi: không tìm thấy tập trạng thái kết"
    assert data["delta"], "Lỗi: không tìm thấy bảng chuyển trạng thái"

    S = data["S"]
    sigma = data["sigma"]
    S0 = data["S0"]
    F = data["F"]
    delta = data["delta"]
    return Otomat(sigma, S, S0, F, delta)

if __name__ == "__main__":
    filepath = input('Nhập tên file đầu vào: ')
    otomat = input_otomat(filepath)
    print('Tập trạng thái ban đầu: ', otomat.S)
    print('Tập trạng thái kết ban đầu: ', otomat.F)
    print('Bảng chuyển trạng thái ban đầu:')
    print('{:>10}'.format('delta'), end='')
    for symbol in otomat.sigma:
        print('{:>10}'.format(symbol), end='')
    print()

    for state in otomat.S:
        print('{:>10}'.format(state), end='')
        for symbol in otomat.sigma:
            if symbol not in otomat.delta[state]:
                print('{:>10}'.format('-'), end='')
            else:
                print('{:>10}'.format(','.join(otomat.delta[state][symbol])), end='')
        print()

    otomat.minimize()

    print('Tập trạng thái sau tối thiểu hóa: ', otomat.S)
    print('Tập trạng thái kết sau tối thiểu hóa: ', otomat.F)
    print('Bảng chuyển trạng thái sau tối thiểu hóa:')
    print('{:>10}'.format('delta'), end='')
    for symbol in otomat.sigma:
        print('{:>10}'.format(symbol), end='')
    print()

    for state in otomat.S:
        print('{:>10}'.format(state), end='')
        for symbol in otomat.sigma:
            if symbol not in otomat.delta[state]:
                print('{:>10}'.format('-'), end='')
            else:
                print('{:>10}'.format(otomat.delta[state][symbol][0]), end='')
        print()
