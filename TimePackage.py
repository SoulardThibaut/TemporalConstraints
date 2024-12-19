import numpy as np
import copy

class Interval:

    start = np.datetime64 
    end = np.datetime64

    def __init__(self, start:np.datetime64, end:np.datetime64) -> None:
        if  start == None or end == None or start <= end:
            self.start = start
            self.end = end
        else:
            print("Interval inversed !")
            self.start = end
            self.end = start

    def __str__(self) -> str:
        return str((self.start, self.end))
    
    def __repr__(self) -> str:
        return str(self)

    def __hash__(self) -> int:
        return hash((self.start, self.end))

    def _is_valid_operand(self, other):
        return (hasattr(other, "start") * hasattr(other, "end"))

    def __eq__(self, other):
        if not self._is_valid_operand(other):
            return NotImplemented
        return (self.start==other.start) * (self.end==other.end)

    def get_start(self) -> np.datetime64:
        return self.start

    def get_end(self) -> np.datetime64:
        return self.end
    
    def update_start(self, new_start:np.datetime64) -> np.datetime64:
        self.start = new_start
    
    def update_end(self, new_end:np.datetime64) -> np.datetime64:
        self.end = new_end

    def day_in_the_interval(self, entity=None) -> int:
        start = self.start
        if start == None:
            start = entity.life_span.get_start()
        end = self.end 
        if self.end == None:
            end = entity.life_span.get_end()
        return (end - start).astype("D").astype(int)

    #### ALLEN'S AXIOMS

    # The end of A is before the start of B
    def is_A_before(self, other) -> bool:
        return self.get_end() < other.get_start()
    
    # Both intervals are equal
    def is_A_equal(self, other) -> bool:
        return (self.get_start() == other.get_start()) \
            & (self.get_end() == other.get_end())
    
    # The end of A is the start of B 
    def is_A_meets(self, other) -> bool:
        return self.get_end() == other.get_start()
    
    # The end of A is after the start of B & before the end of B
    def is_A_overlaps(self, other) -> bool:
        return (self.get_start() < other.get_start())\
            & (self.get_end() > other.get_start()) \
            & (self.get_end() < other.get_end())
    
    # The start of A is after the start of B and the end of A is before the end of B
    def is_A_during(self, other) -> bool:
        return ((self.get_start() > other.get_start()) & (self.get_end() < other.get_end()))
        # return ((self.get_start() > other.get_start()) & (self.get_end() <= other.get_end())) \
        #     or ((self.get_start() >= other.get_start()) & (self.get_end() < other.get_end()))
    
    # A and B start together but A finishes first
    def is_A_starts(self, other) -> bool:
        return (self.get_start() == other.get_start()) \
            & (self.get_end() < other.get_end())
    
    # B starts before A but finishes with A
    def is_A_finishes(self, other) -> bool:
        return (self.get_start() > other.get_start()) \
            & (self.get_end() == other.get_end())
    
    # Launch every verification of the axioms 
    def is_A_verification(self, other) -> dict():
        return {"before":self.is_A_before(other),
                "equal":self.is_A_equal(other),
                "meets":self.is_A_meets(other),
                "overlaps":self.is_A_overlaps(other),
                "during":self.is_A_during(other),
                "starts":self.is_A_starts(other),
                "finishes":self.is_A_finishes(other)}

class Triple:

    head = str
    relation = str
    value = str
    date = Interval 
    relation_type = str

    def __init__(self, head:str, relation:str, value, date:Interval) -> None:
        self.head = head
        self.relation = relation
        self.value = value
        self.date = date
        
        if (type(value) == type("")) and ((value[:len("http://")] == "http://") or (value[:len("https://")] == "https://")):
            self.relation_type = "Object"
        else:
            self.relation_type = "Datatype"

    def __str__(self) -> str:
        return str((self.head, self.relation, self.value, self.date))
    
    def __repr__(self) -> str:
        return str(self)

    def __hash__(self) -> int:
        return hash((self.head, self.relation, self.value, str(self.date)))
    
    def __eq__(self, other) -> bool:
        return (self.head == other.head) \
            & (self.relation == other.relation) \
            & (self.value == other.value) \
            & (self.date == other.date) \
            & (self.relation_type == other.relation_type)

class Entity:

    name = str
    life_span = Interval
    triples_per_r = dict
    triples_per_r_and_rxv = dict
    today = np.datetime64
    granularity = str


    def __init__(self, name:str, today:np.datetime64, granularity:str) -> None:
        self.name = name
        self.life_span = Interval(None, None)
        self.triples_per_r = {}
        self.triples_per_r_and_rxv = {}
        self.today = today
        self.granularity = granularity 

    def __str__(self) -> str:
        return str((self.name, str(self.life_span)))

    def __repr__(self) -> str:
        return str(self)

    def __hash__(self):
        return hash(self.name)
    
    def add_triple(self, triple:Triple) -> None:

        if not triple.relation in self.triples_per_r:
            self.triples_per_r[triple.relation] = set()
            self.triples_per_r_and_rxv[triple.relation] = set()

        self.triples_per_r[triple.relation].add(triple)
        self.triples_per_r_and_rxv[triple.relation].add(triple)

        ### PREFIX FOR WIKIDATA
        prefix = "http://"
        if triple.value[:len(prefix)] == prefix:
            if not (triple.relation, triple.value) in self.triples_per_r_and_rxv:
                self.triples_per_r_and_rxv[(triple.relation, triple.value)] = set()

            self.triples_per_r_and_rxv[(triple.relation, triple.value)].add(triple)

        # if not triple.value in self.triples_per_r:
        #     self.triples_per_v[triple.value] = set()
        # self.triples_per_v[triple.value].add(triple)
        
        if (triple.date.get_start() != None):
            if (self.life_span.get_start() != None) and\
                    (self.life_span.get_start() > triple.date.get_start()):
                self.life_span.update_start(new_start=triple.date.get_start())
            elif (self.life_span.get_start() == None):
                self.life_span.update_start(new_start=triple.date.get_start())

            if (self.life_span.get_end() != None) and\
                    (self.life_span.get_end() < triple.date.get_start()):
                self.life_span.update_end(new_end=triple.date.get_start()+np.timedelta64(1,self.granularity))
            elif (self.life_span.get_end() == None):
                self.life_span.update_end(new_end=triple.date.get_start()+np.timedelta64(1,self.granularity))

        if (triple.date.get_end() != None):
            if (self.life_span.get_end() != None) and\
                    (self.life_span.get_end() < triple.date.get_end()):
                self.life_span.update_end(new_end=triple.date.get_end())
            elif (self.life_span.get_end() == None):
                self.life_span.update_end(new_end=triple.date.get_end())

            if (self.life_span.get_start() != None) and\
                    (self.life_span.get_start() > triple.date.get_end()):
                self.life_span.update_start(new_start=triple.date.get_end()-np.timedelta64(1,self.granularity))
            elif (self.life_span.get_start() == None):
                self.life_span.update_start(new_start=triple.date.get_end()-np.timedelta64(1,self.granularity))
        else:
            self.life_span.update_end(self.today)

    def remove_triple(self, triple:Triple) -> None:
        
        if triple.relation in self.triples_per_r:

            self.triples_per_r[triple.relation].remove(triple)
            self.triples_per_r_and_rxv[triple.relation].remove(triple)
            
            if len(self.triples_per_r[triple.relation]) == 0:
                self.triples_per_r.pop(triple.relation)
                self.triples_per_r_and_rxv.pop(triple.relation)
        
        if (triple.relation, triple.value) in self.triples_per_r_and_rxv:

            self.triples_per_r_and_rxv[(triple.relation, triple.value)].remove(triple)
            
            if len(self.triples_per_r_and_rxv[(triple.relation, triple.value)]) == 0:
                self.triples_per_r_and_rxv.pop((triple.relation, triple.value))

    def update_lifespan(self) -> None:

        new_early = None
        new_latest = None

        for r in self.triples_per_r:
            for t in self.triples_per_r[r]:
                if new_early == None and t.date.get_start() != None:
                    new_early = t.date.get_start()
                elif t.date.get_start() != None and new_early>t.date.get_start():
                    new_early = t.date.get_start()
                elif t.date.get_end() != None and (new_early == None or new_early>t.date.get_end()-np.timedelta64(1,self.granularity)):
                    new_early = t.date.get_end()-np.timedelta64(1,self.granularity)
                
                if t.date.get_end() == None:
                    new_latest = self.today
                elif new_latest == None:
                    new_latest = t.date.get_end()
                elif new_latest < t.date.get_end():
                    new_latest = t.date.get_end()
        
        self.life_span = Interval(new_early, new_latest)


    def get_lifespan(self):
        return self.life_span
    
    def get_number_of_days(self):
        return self.life_span.day_in_the_interval()
    
    def get_triples_with_r(self, r):
        if r in self.triples_per_r:
            return self.triples_per_r[r]
        return None
    
    # def get_triples_with_v(self, v):
    #     if v in self.triples_per_v:
    #         return self.triples_per_v[v]
    #     return None

    def generate_triples_per_r_and_rxv(self, rxv_allowed):
        self.triples_per_r_and_rxv = copy.deepcopy(self.triples_per_r)

        for r in self.triples_per_r:
            for t in self.triples_per_r[r]:
                v = t.value
                if (r,v) in rxv_allowed:
                    if not (r,v) in self.triples_per_r_and_rxv:
                        self.triples_per_r_and_rxv[(r,v)] = set()
                    self.triples_per_r_and_rxv[(r,v)].add(t)

    def generate_all_triples_per_r_and_rxv(self):
        self.triples_per_r_and_rxv = copy.deepcopy(self.triples_per_r)

        for r in self.triples_per_r:
            for t in self.triples_per_r[r]:
                v = t.value
                if not (r,v) in self.triples_per_r_and_rxv:
                    self.triples_per_r_and_rxv[(r,v)] = set()
                self.triples_per_r_and_rxv[(r,v)].add(t)

class TimeSequence:

    intervals = list
    multi_valuation_temporal = bool
    meets = None

    def __init__(self, intervals) -> None:

        self.intervals = intervals
        self.multi_valuation_temporal = False
        self.meets = 0

        for i in range(len(intervals)-1):

            if intervals[i].get_end() > intervals[i+1].get_start():
                self.multi_valuation_temporal = True

            if self.intervals[i].is_A_meets(self.intervals[i+1]):
                self.meets += 1
    
    def __len__(self) -> int:
        return len(self.intervals)

    # Maybe to move to the next class
    def find_inter_comparison(self, other) :
        if self.multi_valuation_temporal or other.multi_valuation_temporal:
            print("Working on multi")

        if (len(self.intervals) == 0) or (len(other.intervals) == 0):
            print("One is len == 0")
            return [] 
        # print(self.intervals, other.intervals)

        # Take the last index and try to find the next earliest interval among the two sequence
        # Return name_sequence, new_last_index_per_seq, interval
        # If name_sequence == 2, then we return two intervals because they start at the same time
        def find_next_earliest_interval(last_index_per_seq):
            self_index, other_index = last_index_per_seq
           
            # If we are at the end of one of them then we return the other one directly
            if (self_index+1 >= len(self.intervals)) and (other_index+1 >= len(other.intervals)):
                return -1, None, None
            elif self_index+1 >= len(self.intervals):
                return 1, (self_index,other_index+1), other.intervals[other_index+1]
            elif other_index+1 >= len(other.intervals):
                return 0, (self_index+1,other_index), self.intervals[self_index+1]

            if self.intervals[self_index+1].get_start() < other.intervals[other_index+1].get_start():
                return 0, (self_index+1,other_index), self.intervals[self_index+1]
            elif self.intervals[self_index+1].get_start() > other.intervals[other_index+1].get_start():
                return 1, (self_index,other_index+1), other.intervals[other_index+1]
            elif self.intervals[self_index+1].get_start() == other.intervals[other_index+1].get_start():
                return 2, (self_index+1,other_index+1), (self.intervals[self_index+1], other.intervals[other_index+1])
        
        # We look at which cursor to move
        # Either 0, 1 or 2 (meaning both have to move because they finish at the same time)
        def which_cursor_to_move(c_0, c_1):
            if c_0[2].get_end() < c_1[2].get_end():
                return 0
            elif c_0[2].get_end() > c_1[2].get_end():
                return 1
            elif c_0[2].get_end() == c_1[2].get_end():
                return 2

        last_index_per_seq = [-1, -1]
        # (Index, Seq_name, Interval)
        c_0 = (None, None, None)
        c_1 = (None, None, None)

        # INIT CURSORS
        name_sequence, last_index_per_seq, interval = find_next_earliest_interval(last_index_per_seq)
        if name_sequence == -1:
            return [], []
        elif name_sequence != 2:
            c_0 = (last_index_per_seq[name_sequence], name_sequence, interval)
        else:
            c_0 = (last_index_per_seq[0], 0, interval[0])
            c_1 = (last_index_per_seq[1], 1, interval[1])
        
        # If we are not in the case where we have an equality in the first interval
        if c_1[0] == None:
            name_sequence, last_index_per_seq, interval = find_next_earliest_interval(last_index_per_seq)
            if name_sequence != 2:
                c_1 = (last_index_per_seq[name_sequence], name_sequence, interval)
            else:
                c_0 = (last_index_per_seq[0], 0, interval[0])
                c_1 = (last_index_per_seq[1], 1, interval[1])

        comparisons = []
        while (True):

            if c_0[1] != c_1[1]:
                if c_0[1] == 0:
                    comparisons.append((c_0[2], c_1[2]))
                else:
                    comparisons.append((c_1[2], c_0[2]))

            c_to_move = which_cursor_to_move(c_0, c_1)
            if c_to_move == 0:
                name_sequence, last_index_per_seq, interval = find_next_earliest_interval(last_index_per_seq)
                if name_sequence == -1:
                    break
                elif name_sequence != 2:
                    c_0 = (last_index_per_seq[name_sequence], name_sequence, interval)
                else:
                    c_0 = (last_index_per_seq[0], 0, interval[0])
                    c_1 = (last_index_per_seq[1], 1, interval[1])
            
            elif c_to_move == 1:
                name_sequence, last_index_per_seq, interval = find_next_earliest_interval(last_index_per_seq)
                if name_sequence == -1:
                    break
                elif name_sequence != 2:
                    c_1 = (last_index_per_seq[name_sequence], name_sequence, interval)
                else:
                    c_0 = (last_index_per_seq[0], 0, interval[0])
                    c_1 = (last_index_per_seq[1], 1, interval[1])
            
            # If both cursors are to be moved
            else:
                name_sequence, last_index_per_seq, interval = find_next_earliest_interval(last_index_per_seq)
                if name_sequence == -1:
                    break
                elif name_sequence != 2:
                    c_0 = (last_index_per_seq[name_sequence], name_sequence, interval)
                    
                    name_sequence, last_index_per_seq, interval = find_next_earliest_interval(last_index_per_seq)
                    if name_sequence == -1:
                        break
                    elif name_sequence != 2:
                        c_1 = (last_index_per_seq[name_sequence], name_sequence, interval)
                    else:
                        c_0 = (last_index_per_seq[0], 0, interval[0])
                        c_1 = (last_index_per_seq[1], 1, interval[1])
                else:
                    c_0 = (last_index_per_seq[0], 0, interval[0])
                    c_1 = (last_index_per_seq[1], 1, interval[1])
        
        return comparisons

class TimeSequenceRelation:

    name_axioms = {
        "equal", "before", 
        "meets", "overlaps", 
        "during", "starts", 
        "finishes"
    }
        
    name_relation_A = str
    name_relation_B = str

    seq_A = TimeSequence
    seq_B = TimeSequence

    inter_comparison_A_to_B = dict
    inter_comparison_B_to_A = dict

    A_o_B = set
    B_o_A = set

    verified = bool

    def __init__(self, name_relation_A, name_relation_B, seq_A, seq_B, constraint_to_check=None) -> None:
        name_relation_A = str(name_relation_A)
        name_relation_B = str(name_relation_B)

        if name_relation_A < name_relation_B:
            self.name_relation_A = name_relation_A
            self.name_relation_B = name_relation_B

            self.seq_A = seq_A
            self.seq_B = seq_B

        else:
            self.name_relation_A = name_relation_B
            self.name_relation_B = name_relation_A

            self.seq_A = seq_B
            self.seq_B = seq_A

        compare = self.seq_A.find_inter_comparison(self.seq_B)

        inter_raw_a_to_b = [int_a.is_A_verification(int_b) for (int_a, int_b) in compare]
        inter_raw_b_to_a = [int_b.is_A_verification(int_a) for (int_a, int_b) in compare]

        self.inter_comparison_A_to_B = {key:sum([inter_raw_a_to_b[i][key] for i in range(len(inter_raw_a_to_b))]) for key in self.name_axioms}
        self.inter_comparison_B_to_A = {key:sum([inter_raw_b_to_a[i][key] for i in range(len(inter_raw_b_to_a))]) for key in self.name_axioms}


        self.A_o_B = set()
        self.B_o_A = set()

        if not constraint_to_check: # Constraint at None
            self.verify_axioms_props()
            self.verify_multi_axioms_props()
            # self.verify_multi_axioms_props_restrictif()
        else:
            self.verified = self.apply_only_constraint(constraint_to_check)

    def get_name(self):
        return (self.name_relation_A, self.name_relation_B)

    # Axioms relations

    def is_A_equal_B(self):
        if (self.inter_comparison_A_to_B["equal"] == len(self.seq_A.intervals)):
            return "equal_axiom"
        return ""

    def is_A_before_B(self):
        if (self.inter_comparison_A_to_B["before"] == len(self.seq_A.intervals)):
            return "before"
        return ""
    
    def is_A_meets_B(self):
        if (self.inter_comparison_A_to_B["meets"] == len(self.seq_A.intervals)):
            return "meets"
        return ""

    def is_A_overlaps_B(self):
        if (self.inter_comparison_A_to_B["overlaps"] == len(self.seq_A.intervals)):
            return "overlaps"
        return ""
    
    def is_A_during_B(self):
        if (self.inter_comparison_A_to_B["during"] == len(self.seq_A.intervals)):
            return "during"
        return ""
    
    def is_A_starts_B(self):
        if (self.inter_comparison_A_to_B["starts"] == len(self.seq_A.intervals)):
            return "starts"
        return ""
    
    def is_A_finishes_B(self):
        if (self.inter_comparison_A_to_B["finishes"] == len(self.seq_A.intervals)):
            return "finishes"
        return ""

    def is_B_equal_A(self):
        if (self.inter_comparison_B_to_A["equal"] == len(self.seq_B.intervals)):
            return "equal_axiom"
        return ""
    
    def is_B_before_A(self):
        if (self.inter_comparison_B_to_A["before"] == len(self.seq_B.intervals)):
            return "before"
        return ""
    
    def is_B_meets_A(self):
        if (self.inter_comparison_B_to_A["meets"] == len(self.seq_B.intervals)):
            return "meets"
        return ""

    def is_B_overlaps_A(self):
        if (self.inter_comparison_B_to_A["overlaps"] == len(self.seq_B.intervals)):
            return "overlaps"
        return ""
    
    def is_B_during_A(self):
        if (self.inter_comparison_B_to_A["during"] == len(self.seq_B.intervals)):
            return "during"
        return ""
    
    def is_B_starts_A(self):
        if (self.inter_comparison_B_to_A["starts"] == len(self.seq_B.intervals)):
            return "starts"
        return ""
    
    def is_B_finishes_A(self):
        if (self.inter_comparison_B_to_A["finishes"] == len(self.seq_B.intervals)):
            return "finishes"
        return ""
    
    def are_equal(self):
        return (self.inter_comparison_A_to_B["equal"] == len(self.seq_A.intervals))  and \
            (self.inter_comparison_B_to_A["equal"] == len(self.seq_B.intervals)) 
    
    def verify_axioms_props(self):

        if self.are_equal():
            self.A_o_B.add("are equals")
            self.B_o_A.add("are equals")


        fct_A_o_B = [self.is_A_equal_B,\
                     self.is_A_before_B, self.is_A_meets_B, \
                     self.is_A_overlaps_B, self.is_A_during_B,\
                     self.is_A_starts_B, self.is_A_finishes_B]
        
        for fct in fct_A_o_B:
            res = fct()
            if res:
                self.A_o_B.add(res)

        fct_B_o_A = [self.is_B_equal_A,\
                     self.is_B_before_A, self.is_B_meets_A, \
                     self.is_B_overlaps_A, self.is_B_during_A,\
                     self.is_B_starts_A, self.is_B_finishes_A]
        

        for fct in fct_B_o_A:
            res = fct()
            if res:
                self.B_o_A.add(res)

    # Multi axions relations

    def is_either_one_or_the_other(self):
        # FOR ALL axioms/{before, meets}, _ axioms _ == 0 

        sum_axioms = 0
        for axiom in self.name_axioms.difference({"before", "meets"}):
            sum_axioms += self.inter_comparison_A_to_B[axiom]
            sum_axioms += self.inter_comparison_B_to_A[axiom]

        if sum_axioms == 0:
            return "either_one_or_the_other"
        
        return ""

    # def is_one_or_the_other_not_closed(self):
    #     # FOR ALL axioms/{before}, _ axioms _ == 0 

    #     sum_axioms = 0
    #     for axiom in self.name_axioms.difference({"before"}):
    #         sum_axioms += self.inter_comparison_A_to_B[axiom]
    #         sum_axioms += self.inter_comparison_B_to_A[axiom]

    #     if sum_axioms == 0:
    #         return "one_or_the_other_not_closed"
    #     return ""
    
    def is_one_or_the_other_not_closed(self):
        # FOR ALL axioms/{before}, _ axioms _ == 0 

        if self.seq_A.meets+self.seq_B.meets != 0:
            return ""
        
        sum_axioms = 0
        for axiom in self.name_axioms.difference({"before"}):
            sum_axioms += self.inter_comparison_A_to_B[axiom]
            sum_axioms += self.inter_comparison_B_to_A[axiom]

        if sum_axioms == 0:
            return "one_or_the_other_not_closed"
        return ""

    # def is_one_or_the_other_closed(self):
    #     # FOR ALL axioms/{meets}, _ axioms _ == 0 

    #     sum_axioms = 0
    #     for axiom in self.name_axioms.difference({"meets"}):
    #         sum_axioms += self.inter_comparison_A_to_B[axiom]
    #         sum_axioms += self.inter_comparison_B_to_A[axiom]

    #     if sum_axioms == 0:
    #         return "one_or_the_other_closed"
    #     return ""

    def is_one_or_the_other_closed(self):
        # FOR ALL axioms/{meets}, _ axioms _ == 0 

        sum_axioms = 0
        for axiom in self.name_axioms.difference({"meets"}):
            sum_axioms += self.inter_comparison_A_to_B[axiom]
            sum_axioms += self.inter_comparison_B_to_A[axiom]

        if sum_axioms == 0:
            return "one_or_the_other_closed"
        return ""
    
    def is_in_between(self):
        if ((self.inter_comparison_A_to_B["before"]+self.inter_comparison_B_to_A["before"]) \
            == (len(self.seq_A.intervals) + len(self.seq_B.intervals) - 1)):
            return "in_between"
        return ""
    
    def is_in_between_closed(self):
        if ((self.inter_comparison_A_to_B["meets"]+self.inter_comparison_B_to_A["meets"]) \
            ==  (len(self.seq_A.intervals) + len(self.seq_B.intervals) - 1)):
            return "in_between_closed"
        return ""
    
    def is_seq_A_before_seq_B(self):
        if (self.inter_comparison_A_to_B["before"] == 1) &\
               (sum(self.inter_comparison_A_to_B.values()) == 1) &\
               (sum(self.inter_comparison_B_to_A.values()) == 0):
            return "sequence_before"
        return ""
    
    def is_seq_B_before_seq_A(self):
        if (self.inter_comparison_B_to_A["before"] == 1) &\
               (sum(self.inter_comparison_B_to_A.values()) == 1) &\
               (sum(self.inter_comparison_A_to_B.values()) == 0):
            return "sequence_before"
        return ""
    
    def is_seq_A_meets_seq_B(self):
        if (self.inter_comparison_A_to_B["meets"] == 1) &\
               (sum(self.inter_comparison_A_to_B.values()) == 1) &\
               (sum(self.inter_comparison_B_to_A.values()) == 0):
            return "sequence_meets"
        return ""
    
    def is_seq_B_meets_seq_A(self):
        if (self.inter_comparison_B_to_A["meets"] == 1) &\
               (sum(self.inter_comparison_B_to_A.values()) == 1) &\
               (sum(self.inter_comparison_A_to_B.values()) == 0):
            return "sequence_meets"
        return ""
    
    def is_seq_A_always_with_seq_B(self):
        if (self.inter_comparison_A_to_B["equal"] + self.inter_comparison_A_to_B["during"] +\
            self.inter_comparison_A_to_B["starts"] + self.inter_comparison_A_to_B["finishes"])\
             ==  len(self.seq_A):
            return "always_with"
        return ""
    
    def is_seq_B_always_with_seq_A(self):
        if (self.inter_comparison_B_to_A["equal"] + self.inter_comparison_B_to_A["during"] +\
            self.inter_comparison_B_to_A["starts"] + self.inter_comparison_B_to_A["finishes"])\
             ==  len(self.seq_B):
            return "always_with"
        return ""
    
    def is_always_overlapping(self):
        if (self.inter_comparison_A_to_B["overlaps"] + self.inter_comparison_B_to_A["overlaps"])\
             ==  len(self.seq_A)+len(self.seq_B)-1:
            return "always_overlapping"
        return ""
    
    # def is_never_alone(self):
    #     sum_axioms = 0
    #     for axiom in self.name_axioms.difference({"before", "meets"}):
    #         sum_axioms += self.inter_comparison_A_to_B[axiom]
    #         sum_axioms += self.inter_comparison_B_to_A[axiom]
        
    #     if sum_axioms == (len(self.seq_A) + len(self.seq_B) - 1):
    #         return "never alone"
    #     return ""

    def verify_multi_axioms_props(self):

        fcts = [
                self.is_either_one_or_the_other, self.is_one_or_the_other_not_closed,\
                self.is_one_or_the_other_closed, self.is_in_between,\
                self.is_in_between_closed, self.is_always_overlapping\
                # self.is_never_alone
                ]
        
        fcts_A_o_B = [self.is_seq_A_before_seq_B, self.is_seq_A_meets_seq_B,\
                       self.is_seq_A_always_with_seq_B]
        fcts_B_o_A = [self.is_seq_B_before_seq_A, self.is_seq_B_meets_seq_A,\
                       self.is_seq_B_always_with_seq_A]
        for fct in fcts:
            res = fct()
            if res:
                self.A_o_B.add(res)
                self.B_o_A.add(res)

        for fct in fcts_A_o_B:
            res = fct()
            if res:
                self.A_o_B.add(res)

        for fct in fcts_B_o_A:
            res = fct()
            if res:
                self.B_o_A.add(res)

    def verify_multi_axioms_props_restrictif(self):

        ### ETIHER ONE OR THE OTHER
        ### __ CLOSED ||| ___ NOT CLOSED
        ### In between closed |||| In between | A seq before  

        ##### A SEQ BEFORE 

        res = self.is_seq_A_before_seq_B()
        if res:
            self.A_o_B.add(res)
            return 
        
        res = self.is_seq_B_before_seq_A()
        if res:
            self.B_o_A.add(res)
            return 
        
        ##### In between 

        res = self.is_in_between()
        if res:
            self.A_o_B.add(res)
            self.B_o_A.add(res)
            return 
        
        ##### In between closed 

        res = self.is_in_between_closed()
        if res:
            self.A_o_B.add(res)
            self.B_o_A.add(res)
            return 
        
        ##### is_one_or_the_other_not_closed

        res = self.is_one_or_the_other_not_closed()
        if res:
            self.A_o_B.add(res)
            self.B_o_A.add(res)
            return 
        
         ##### is_one_or_the_other_closed

        res = self.is_one_or_the_other_closed()
        if res:
            self.A_o_B.add(res)
            self.B_o_A.add(res)
            return 
        
         ##### is_either_one_or_the_other

        res = self.is_either_one_or_the_other()
        if res:
            self.A_o_B.add(res)
            self.B_o_A.add(res)
            return 
        
    def apply_only_constraint(self, constraint):
        nc = constraint.get_r()

        if nc == "either_one_or_the_other":
            return self.is_either_one_or_the_other() != ""
        elif nc == "one_or_the_other_not_closed":
            return self.is_one_or_the_other_not_closed() != ""
        elif nc == "one_or_the_other_closed":
            return self.is_one_or_the_other_closed() != ""
        elif nc == "in_between_closed":
            return self.is_in_between_closed() != ""
        elif nc == "in_between":
            return self.is_in_between() != ""
        elif nc == "always_overlapping":
            return self.is_always_overlapping() != ""

        if constraint.get_a() == self.name_relation_A:
            if nc == "equal_axiom":
                return self.is_A_equal_B() != ""
            elif nc == "before":
                return self.is_A_before_B() != ""
            elif nc == "meets":
                return self.is_A_meets_B() != ""
            elif nc == "overlaps":
                return self.is_A_overlaps_B() != ""
            elif nc == "during":
                return self.is_A_during_B() != ""
            elif nc == "starts":
                return self.is_A_starts_B() != ""
            elif nc == "finishes":
                return self.is_A_finishes_B() != ""
            elif nc == "sequence_before":
                return self.is_seq_A_before_seq_B() != ""
            elif nc == "sequence_meets":
                return self.is_seq_A_meets_seq_B() != ""
            elif nc == "always_with":
                return self.is_seq_A_always_with_seq_B() != ""
            else:
                print(f"I am not handled : {constraint}")
                return None

        else:
            if nc == "equal_axiom":
                return self.is_B_equal_A() != ""
            elif nc == "before":
                return self.is_B_before_A() != ""
            elif nc == "meets":
                return self.is_B_meets_A() != ""
            elif nc == "overlaps":
                return self.is_B_overlaps_A() != ""
            elif nc == "during":
                return self.is_B_during_A() != ""
            elif nc == "starts":
                return self.is_B_starts_A() != ""
            elif nc == "finishes":
                return self.is_B_finishes_A() != ""
            elif nc == "sequence_before":
                return self.is_seq_B_before_seq_A() != ""
            elif nc == "sequence_meets":
                return self.is_seq_B_meets_seq_A() != ""
            elif nc == "always_with":
                return self.is_seq_B_always_with_seq_A() != ""
            else:
                print(f"I am not handled : {constraint}")
                return None

class TemporalRule:

    a = str
    precision_a = str
    r = str
    b = str
    precision_b = str

    error_percentage = float
    coverage_percentage = float

    def __init__(self, a:str, precision_a:str, r:str, b:str, precision_b:str, error_percentage:float, coverage_percentage:float) -> None:

        self.a = a
        self.precision_a = precision_a

        self.r = r

        self.b = b
        self.precision_b = precision_b
        

        self.error_percentage = error_percentage
        self.coverage_percentage = coverage_percentage

    def __str__(self) -> str:
        res = ""
        if not self.precision_a:
            res+=f"{self.a} "
        else:
            res+=f"{self.a} X {self.precision_a} "

        res+=f"{self.r} "

        if not self.precision_b:
            res+=f"{self.b} "
        else:
            res+=f"{self.b} X {self.precision_b} "

        return res+f": [e:{self.error_percentage}, c:{self.coverage_percentage}]"

    def __repr__(self) -> str:
        return str(self)
    
    def __hash__(self) -> int:
        res = self.a
        if self.precision_a:
            res += "X"+self.precision_a
        res += " "+self.r+" "
        res += self.b
        if self.precision_b:
            res += "X"+self.precision_b
        return hash(res)

    def __eq__(self, other) -> bool:
        return self.a == other.a \
            and self.precision_a == other.precision_a \
            and self.r == other.r\
            and self.b == other.b\
            and self.precision_b == other.precision_b

    # def get_a(self):
    #     res = self.a
    #     if self.precision_a:
    #         res+="X"+self.precision_a
    #     return res

    def get_a(self):
        if not self.precision_a:
            return self.a
        else:
            return (self.a, self.precision_a)

    # def get_b(self):
    #     res = self.b
    #     if self.precision_b:
    #         res+="X"+self.precision_b
    #     return res
    
    def get_b(self):
        if not self.precision_b:
            return self.b
        else:
            return (self.b, self.precision_b)

    def get_r(self):
        return self.r

    def to_tsv(self) -> str:
        res = ""

        if not self.precision_a:
            res+=f"{self.a}\t"
        else:
            res+=f"({self.a}, {self.precision_a})\t"

        res+=f"{self.r}\t"

        if not self.precision_b:
            res+=f"{self.b}\t"
        else:
            res+=f"({self.b}, {self.precision_b})\t"

        return res+f"{self.error_percentage}\t{self.coverage_percentage}"

    def load_a_rule(line:str):
        line_splited = line.split("\t")
        if len(line_splited) != 5:
            print("ERROR LOAD NOT A TEMPORAL RULE LINE")

        if "," in line_splited[0]:
            a = line_splited[0].split(", ")[0][2:-1]
            precision_a = line_splited[0].split(", ")[1][1:-2]
        else:
            a = line_splited[0]
            precision_a = None
        
        if "," in line_splited[2]:
            b = line_splited[2].split(", ")[0][2:-1]
            precision_b = line_splited[2].split(", ")[1][1:-2]
        else:
            b = line_splited[2]
            precision_b = None
        return TemporalRule(a, precision_a, line_splited[1], b, precision_b,\
                            float(line_splited[3]), float(line_splited[4]))
    
    def is_useful_for_e(self, e:Entity) -> bool:
        # We look if we can use the A part
        if not self.precision_a:
            if not e.get_triples_with_r(self.a):
                return False
        else:
            triples = e.get_triples_with_r(self.a)
            if not triples:
                return False
            else:
                i = 0
                found_v = False
                while((not found_v) and (i < len(triples))):
                    if triples[i].value == self.precision_a:
                        found_v = True
                    i+=1
                if not found_v :
                    return False
        
        # We look if we can use the B part
        if not self.precision_b:
            if not e.get_triples_with_r(self.b):
                return False
        else:
            triples = e.get_triples_with_r(self.b)
            if not triples:
                return False
            else:
                i = 0
                found_v = False
                while((not found_v) and (i < len(triples))):
                    if triples[i].value == self.precision_b:
                        found_v = True
                    i+=1
                if not found_v :
                    return False
        
        # We can use both parts
        return True

    # def does_hold_for_e(self, e:Entity) -> bool:

def ordered_timeline_of_r_mono_value_per_int(entity:Entity, r:str):

    triples_of_r = entity.get_triples_with_r(r)

    r_per_start = {(t.date.get_start() if t.date.get_start() != None else entity.get_lifespan().get_start()):t  for t in triples_of_r}
    
    return [(r_per_start[start], start) for start in sorted(r_per_start.keys())]

def ordered_time_sequence_first_start(entity:Entity, r:str):
    triples_of_r = entity.get_triples_with_r(r)
    if triples_of_r != None:
        r_per_start = {}
        for t in triples_of_r:

            start_triple, end_triple = t.date.get_start(), t.date.get_end()
            
            if start_triple == None:
                start_triple = entity.get_lifespan().get_start()

            if end_triple == None:
                end_triple = entity.get_lifespan().get_end()

            if not start_triple in r_per_start:
                r_per_start[start_triple] = set()

            r_per_start[start_triple].add(Interval(start_triple, end_triple))
        
        return [i for start in sorted(r_per_start.keys()) for i in r_per_start[start]]

    return []

def ordered_time_sequence_first_start_with_rxv(entity:Entity, r):
    if r in entity.triples_per_r_and_rxv:
        r_per_start = {}
        triples_of_r = entity.triples_per_r_and_rxv[r]
        for t in triples_of_r:

            start_triple, end_triple = t.date.get_start(), t.date.get_end()
            
            if start_triple == None:
                start_triple = entity.get_lifespan().get_start()

            if end_triple == None:
                end_triple = entity.get_lifespan().get_end()

            if not start_triple in r_per_start:
                r_per_start[start_triple] = set()

            r_per_start[start_triple].add(Interval(start_triple, end_triple))
        
        return [i for start in sorted(r_per_start.keys()) for i in r_per_start[start]]

    return []

def ordered_time_sequence_first_start_with_rxv_return_triples(entity:Entity, r):
    if r in entity.triples_per_r_and_rxv:
        r_per_start = {}
        triples_of_r = entity.triples_per_r_and_rxv[r]
        for t in triples_of_r:

            start_triple, end_triple = t.date.get_start(), t.date.get_end()
            
            if start_triple == None:
                start_triple = entity.get_lifespan().get_start()

            if end_triple == None:
                end_triple = entity.get_lifespan().get_end()

            if not start_triple in r_per_start:
                r_per_start[start_triple] = set()

            r_per_start[start_triple].add(t)
        
        return [t for start in sorted(r_per_start.keys()) for t in r_per_start[start]]

    return []

complex_order = {
    "either_one_or_the_other":0, 
    "one_or_the_other_not_closed":1,
    "one_or_the_other_closed":1,
    "always_with":1,
    "always_overlapping":1,
    "in_between_closed":2,
    "sequence_meets":2,
    "in_between":2,
    "sequence_before":2,
    "are equals":2
}

def remove_useless_complex_rules(rules):
    already_seen_complex = {}
    already_seen_axiom = {}
    for rule in rules:
        a = rule.get_a()
        b = rule.get_b()
        r = rule.get_r()
        if r in complex_order:
            # if not (b, a) in already_seen_complex:
            if (a, b) in already_seen_complex:
                if already_seen_complex[(a, b)][0] < complex_order[r]:
                    already_seen_complex[(a, b)] = (complex_order[r], set([rule]))
                elif already_seen_complex[(a, b)][0] == complex_order[r]:
                    already_seen_complex[(a, b)][1].add(rule)
                    # print("Something strange in complex")
                    # print((a, b))
                    # print(already_seen_complex[(a, b)])
                    # print(r)
            else:
                already_seen_complex[(a, b)] = (complex_order[r], set([rule]))
        else:
            if (a, b) in already_seen_axiom:
                print("Something stange in axiom")
                print((a, b))
                print(already_seen_axiom[(a, b)])
                print(r)
            else:
                already_seen_axiom[(a, b)] = rule
    
    already_seen_complex_final = {}
    for (a, b) in already_seen_complex:
        # if (b, a) in already_seen_complex:
        #     if already_seen_complex[(a, b)][0] > already_seen_complex[(b, a)][0]:
        #         already_seen_complex_final[(a, b)] = already_seen_complex[(a, b)][1]
        #     elif already_seen_complex[(a, b)][0] == already_seen_complex[(b, a)][0]:
        #         already_seen_complex_final[(a, b)] = already_seen_complex[(a, b)][1]
        # else:
        already_seen_complex_final[(a, b)] = already_seen_complex[(a, b)][1]
    
    return set(already_seen_axiom.values()).union(set([complex_rule for set_of_complex_rule in already_seen_complex_final.values() for complex_rule in set_of_complex_rule]))
