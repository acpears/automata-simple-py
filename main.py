from PySimpleAutomata import automata_IO
import os

def bool_combs(n):
    if not n:
        return [[]]
    result = []
    for comb in bool_combs(n-1):
        result.append(comb + [1])
        result.append(comb + [0])
    return result

def setListToString(list):
    if(list == None): return "N/A"
    temp = "{"
    count = len(list)
    for el in list:
        temp += el
        if(count > 1):
            temp += ","
        count -= 1
    temp += "}"
    return temp

class TransTable:
    def __init__(self):
        self.alphabet = []
        
        self.states = []
        self.initState = []
        self.acceptStates = []
        self.transTable = {}
        
        self.pSetStates = []
        self.pSetStatesStrFormat = []
        self.pSetAcceptStates = []
        self.pSetTransTable = {}

        self.dfaStates = []
        self.dfaInitState = []
        self.dfaAcceptStates = []
        self.dfaTransTable = {}

    def addState(self,s):
        if(type(s) == str):
            self.states.append(s)
            self.states.sort()
        if(type(s) == list):
            self.states = s
            self.states.sort()

    def addAlphabet(self,a):
        if(type(a) == str):
            self.alphabet.append(a)
            self.alphabet.sort()
        if(type(a) == list):
            self.alphabet = a
            self.alphabet.sort()

    def addInitState(self,s):
        if(type(s) == str):
            self.initState.append(s)
            self.initState.sort()
        if(type(s) == list):
            self.initState = s
            self.initState.sort()
    
    def addAcceptingState(self,s):
        if(type(s) == str):
            self.acceptStates.append(s)
            self.acceptStates.sort()
        if(type(s) == list):
            self.acceptStates = s
            self.acceptStates.sort()

    def genEmptyTransTable(self):
        for s in self.states:
            self.transTable[s] = {}
            for a in self.alphabet:
                self.transTable[s][a] = []

    def addTrans(self,s,a,tState):
        if(tState not in self.states):
            return False
        if(s in self.transTable.keys()):
            if(a in self.transTable[s].keys()):
                if tState not in self.transTable[s][a]:
                    self.transTable[s][a].append(tState)
                    self.transTable[s][a].sort()
                return True
        return False

# Generates the power set of nfa states
    def genPowerSet(self):
        n = len(self.states) #number of states
        combinations = bool_combs(n)
        
        for comb in combinations:
            temp = []
            index = 0;
            for bit in comb:
                if bit:
                    temp.append(self.states[index])
                index += 1
            
            # generate the list of accepting states within the power set
            for s in temp:
                if s in self.acceptStates:
                    self.pSetAcceptStates.append(setListToString(temp)) # use string format for this list
                    break

            self.pSetStates.append(temp) #formated as a list e.g. [s0,s1,s2]
            self.pSetStatesStrFormat.append(setListToString(temp)) # formated as a string e.g. "{s0,s1,s2}""
        self.pSetStates.sort(key=len) # sorts our power set in the proper order for the table      

# Generates the powerset transition table
    def genPSetTransTable(self):
        for pState in self.pSetStates:
            
            key = setListToString(pState) # format power set to string for trans table
            self.pSetTransTable[key] = {} # create new dictionary for this key
            
            for a in self.alphabet:
                temp = []
                # checks each states of the power set state and adds their transition state to the list
                for s in pState:
                    s1 = set(self.transTable[s][a])
                    s2 = set(temp)
                    temp = list(s2.union(s1))

                temp.sort() # sort for consistency
                self.pSetTransTable[key][a] = temp # adds the transition states for the power set state to the transition table 

# Generates the automaton for the NFA to DFA
    def genDFA(self):
        # recursive method to determine DFA states
        def recur(state):
            for a in self.alphabet:
                temp = self.pSetTransTable[state][a]
                if temp: # skip if list is empty for transition 
                    temp = setListToString(temp) # format list to string
                    if temp in self.dfaStates: 
                        continue # if state is already contained it dfa states then skip
                    self.dfaStates.append(temp)
                    recur(temp)


        init = setListToString(self.initState)
        self.dfaInitState.append(init) # the dfa initial state is the same as the nfa
        self.dfaStates.append(init)
        recur(init) # recursively call the inital state to determine all states of the dfa
        # initial state

        # uses the powerset transition table to generate the dfa transition table
        for s in self.dfaStates:
            self.dfaTransTable[s] = self.pSetTransTable[s]

        # find the dfa accepting states from the power set accepting states
        for s in self.dfaStates:
            if s in self.pSetAcceptStates:
                self.dfaAcceptStates.append(s)

#Methods to generate the proper format for the PySimpleAutomata library
    def psaTransFormatPart1(self):
        table = {}
        for s in self.states:
            for a in self.alphabet: 
                key = (s,a)
                if not self.transTable[s][a]: continue
                table[key] = set(self.transTable[s][a])
        return table

    def psaTransFormatPart2(self):
        table = {}
        for s in self.dfaStates:
            for a in self.alphabet:
                key = (s,a)
                if not self.dfaTransTable[s][a]: continue
                table[key] = {setListToString(self.dfaTransTable[s][a])}
        return table

    def psaDictPart1(self):
        temp = {}
        temp["alphabet"] = set(self.alphabet)
        temp["states"] = set(self.states)
        temp["initial_states"] = set(self.initState)
        temp["accepting_states"] = set(self.acceptStates)
        temp["transitions"] = self.psaTransFormatPart1()
        return temp

    def psaDictPart2(self):
        temp = {}
        temp["alphabet"] = set(self.alphabet)
        temp["states"] = set(self.dfaStates)
        temp["initial_states"] = set(self.dfaInitState)
        temp["accepting_states"] = set(self.dfaAcceptStates)
        temp["transitions"] = self.psaTransFormatPart2()
        return temp

    def printTransTable(self):
        spacer1 = 10
        spacer2 = 5
        space1 = " " * (spacer1 - 5)
        space2 = " " * spacer2
        
        # Print table headers
        print("")
        print("", space2, end = " |     ")

        for el in self.alphabet:
            print(el, space1, end = " |     ")
        
        print("")

        for el in self.transTable.keys():
            
            strLen = len(el)
            space2 = " " * (spacer2 - strLen)
            print(el, space2, end = " | ")
            
            for i in self.transTable[el].keys():
                str = setListToString(self.transTable[el][i])
                strLen = len(str)
                space1 = " " * (spacer1 - strLen)
                print(str, space1, end = " | ")
            
            print("")

    def printPSetTransTable(self):
        spacer1 = 15
        spacer2 = 15
        space1 = " " * (spacer1 - 5)
        space2 = " " * spacer2
        
        # Print table headers
        print("\nDFA Transition Table:")
        print("", space2, end = " |     ")

        for el in self.alphabet:
            print(el, space1, end = " |     ")
        
        print("")

        for el in self.pSetTransTable.keys():
            
            strLen = len(el)

            if el in self.pSetAcceptStates: 
                print("*", end = "")
                strLen += 1
            
            if el == setListToString(self.initState):
                print("->", end = "")
                strLen += 2

            space2 = " " * (spacer2 - strLen)
            print(el, space2, end = " | ")
            
            for i in self.pSetTransTable[el].keys():
                str = setListToString(self.pSetTransTable[el][i])
                strLen = len(str)
                space1 = " " * (spacer1 - strLen)
                print(str, space1, end = " | ")
            
            print("")



def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\b--- ASSIGNMENT #2 ---\n")
    print("Instructions: \n- Use ',' to seperate multiple values\n")
    
    t1 = TransTable()
    
    temp = input("Input alphabet: ").replace(" ","").split(',')
    t1.addAlphabet(temp)

    temp = input("Input states: ").replace(" ","").split(',')
    t1.addState(temp)

    while(True):
        temp = input("Input initial state (single state): ")

        if temp not in t1.states:
            print(temp, "is not contained in states. Please input one of the following: ", end = "")
            for s in t1.states:
                print(s, end = " ")
            print("")
            continue

        t1.addInitState(temp)
        break
    
    while(True):
        temp = input("Input accepting states: ").replace(" ","").split(',')
        
        validate = True;
        for t in temp:
            if t not in t1.states:
                print(t, "is not a valide state. Try again!")
                validate = False

        if not validate:
            continue

        t1.addAcceptingState(temp)
        break

    t1.genEmptyTransTable()

    print("\nInput Transitions (use the word 'none' to designate no transition state):")
    print("-------------------")
    for s in t1.states:
        for a in t1.alphabet:
            while(True):
                print("Input transition state from ", s, "with input", a, end=" : ")
                tranIn = input("")
                if(tranIn == "none"): 
                    break
                tran = tranIn.split(',')

                validate = True  
                for t in tran:
                    #add input states to the transition table
                    if not t1.addTrans(s,a,t):
                        print(t, "is not a valide state. Try again!")
                        validate = False
                        break
                
                if not validate:
                    continue
                break

    while(True):
        choice = input("\nPlease select problem (1 or 2): ")

        root = os.getcwd()
        folder = "diagrams"
        
        if choice == "1":
            fileName = "diagram_part1"
            p1 = t1.psaDictPart1()
            automata_IO.nfa_to_dot(p1, fileName, folder)
            print("\nTransition diagram: Please check the folder located at "+ root +"/" + folder +" for file \"" + fileName+ ".dot.svg\"\n")
        
        elif choice == "2":
            fileName = "diagram_part2"
            t1.genPowerSet()
            t1.genPSetTransTable()
            t1.genDFA()
            t1.printPSetTransTable()
            p2 = t1.psaDictPart2()
            automata_IO.nfa_to_dot(p2, fileName, folder)
            print("\nTransition diagram: Please check the folder located at "+ root +"/" + folder +" for file \"" + fileName+ ".dot.svg\"\n")
        
            print(t1.dfaStates)
            print(t1.dfaInitState)
            print(t1.dfaAcceptStates)
            print(t1.dfaTransTable)
        else:
            print("Incorrect input. Please input value 1 or 2")
            continue
        break

main()