def maybe_boat_check(self, row, col , val, size):
        if val == "T":
            action = [[row, col, val, size]]
            if (row + size - 1) <= 9:
                if size == 4:
                    v1 = self.get_value(row + 1, col)
                    v2 = self.get_value(row + 2, col)
                    v3 = self.get_value(row + 3, col)
                    if v1 in (None, "M") and  v2 in (None, "M") and v3 in (None, "B"):
                        if v1 == None:
                            action.append([row + 1, col, "M"])
                        if v2 == None:
                            action.append([row + 2, col, "M"])
                        if v3 == None:
                            action.append([row + 3, col, "B"])
                        if self.cant_place_boat("V", col, action):
                            return False
                        return action
                
                if size == 3:
                    v1 = self.get_value(row + 1, col)
                    v2 = self.get_value(row + 2, col)
                    if v1 in (None, "M") and  v2 in (None, "B"):
                        if v1 == None:
                            action.append([row + 1, col, "M"])
                        if v2 == None:
                            action.append([row + 2, col, "B"])
                        if self.cant_place_boat("V", col, action):                     
                            return False
                        return action

                if size == 2:
                    v1 = self.get_value(row + 1, col)
                    if v1 in (None, "B"):
                        if v1 == None:
                            action.append([row + 1, col, "B"])
                        if self.cant_place_boat("V", col, action):                            
                            return False
                        return action
            return False

        elif val == "L":
            action = [[row, col, val, size]]
            if (col + size - 1) <= 9:
                if size == 4:
                    
                    v1 = self.get_value(row, col + 1)
                    v2 = self.get_value(row, col + 2)
                    v3 = self.get_value(row, col + 3)
                    if v1 in (None, "M") and  v2 in (None, "M") and v3 in (None, "R"):
                        if v1 == None:
                            action.append([row, col + 1, "M"])
                        if v2 == None:
                            action.append([row, col + 2, "M"])
                        if v3 == None:
                            action.append([row, col + 3, "R"])
                        if self.cant_place_boat("H", row, action):                            
                            return False
                        return action
                
                if size == 3:
                    
                    v1 = self.get_value(row, col + 1)
                    v2 = self.get_value(row, col + 2)
                    if v1 in (None, "M") and  v2 in (None, "R"):
                        if v1 == None:
                            action.append([row, col + 1, "M"])
                        if v2 == None:
                            action.append([row, col + 2, "R"])
                        if self.cant_place_boat("H", row, action):                            
                            return False
                        return action

                if size == 2:
                    
                    v1 = self.get_value(row, col + 1)
                    if v1 in (None, "R"):
                        if v1 == None:
                            action.append([row, col + 1, "R"])
                        if self.cant_place_boat("H", row, action):                            
                            return False    
                        return action

            return False

        elif val == None:
            if size == 1:
                if (col in self.complete_cols) or (row in self.complete_rows):
                    return False
                else:    
                    action = [[row, col, "C", size], [row, col, "C"]]
                    return action
            if (row + size - 1) <= 9:
                action = [[row, col, "T", size]]
                if size == 4:
                    v1 = self.get_value(row + 1, col)
                    v2 = self.get_value(row + 2, col)
                    v3 = self.get_value(row + 3, col)
                    if v1 in (None, "M") and  v2 in (None, "M") and v3 in (None, "B"):
                        action.append([row, col, "T"])
                        if v1 == None:
                            action.append([row + 1, col, "M"])
                        if v2 == None:
                            action.append([row + 2, col, "M"])
                        if v3 == None:
                            action.append([row + 3, col, "B"])
                        if not self.cant_place_boat("V", col, action):                            
                            return action
                        
                
                if size == 3:
                    v1 = self.get_value(row + 1, col)
                    v2 = self.get_value(row + 2, col)
                    if v1 in (None, "M") and  v2 in (None, "B"):
                        action.append([row, col, "T"])
                        if v1 == None:
                            action.append([row + 1, col, "M"])
                        if v2 == None:
                            action.append([row + 2, col, "B"])
                        if not self.cant_place_boat("V", col, action):                            
                            return action
                        

                if size == 2:
                    v1 = self.get_value(row + 1, col)
                    if v1 in (None, "B"):
                        action.append([row, col, "T"])
                        if v1 == None:
                            action.append([row + 1, col, "B"])
                        if not self.cant_place_boat("V", col, action):                            
                            return action           

            if (col + size - 1) <= 9:
                action = [[row, col, "L", size]]
                if size == 4:
                    v1 = self.get_value(row, col + 1)
                    v2 = self.get_value(row, col + 2)
                    v3 = self.get_value(row, col + 3)
                    if v1 in (None, "M") and  v2 in (None, "M") and v3 in (None, "R"):
                        action.append([row, col, "L"])
                        if v1 == None:
                            action.append([row, col + 1, "M"])
                        if v2 == None:
                            action.append([row, col + 2, "M"])
                        if v3 == None:
                            action.append([row, col + 3, "R"])
                        if self.cant_place_boat("H", row, action):                            
                            return False
                        return action
                
                if size == 3:
                    
                    v1 = self.get_value(row, col + 1)
                    v2 = self.get_value(row, col + 2)
                    if v1 in (None, "M") and  v2 in (None, "R"):
                        action.append([row, col, "L"])
                        if v1 == None:
                            action.append([row, col + 1, "M"])
                        if v2 == None:
                            action.append([row, col + 2, "R"])
                        if self.cant_place_boat("H", row, action):
                                                    
                            return False
                        return action

                if size == 2:
                    v1 = self.get_value(row, col + 1)
                    if v1 in (None, "R"):
                        action.append([row, col, "L"])
                        if v1 == None:
                            action.append([row, col + 1, "R"])
                        if self.cant_place_boat("H", row, action):
                            return False
                        return action
            return False

        elif val == "C":
            self.add_boat_coordinates(row, col, 1)
            return False


boat_types = {1: ["C"], 
            2:{"V":["T", "B"], "H": ["L", "R"]}, 
            3:{"V":["T", "M","B"], "H": ["L", "M", "R"]},
            4:{"V":["T", "M", "M", "B"], "H": ["L", "M", "M", "R"]}}


if val == "T":
    check(row, col, "V", size)





