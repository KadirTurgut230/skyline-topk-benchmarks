def compare_records(record_1, record_2, dimension, mcr_type):
    # mcr_type = 0(minimized), 1(maximized)
    # 0 = non domination, 1 = Record 1 dominates 2, 2 = 2 dominates 1
    is_1_dominated = True
    is_2_dominated = True
    
    if mcr_type == 0 :
        for i in range(1, dimension + 1):
           if record_1['var_' + str(i)] < record_2['var_' + str(i)]:
               is_1_dominated = False
               if is_2_dominated == False :
                   return 0
            
           elif record_2['var_' + str(i)] < record_1['var_' + str(i)]:
               is_2_dominated = False
               if is_1_dominated == False :
                   return 0
               
    else:
        for i in range(1, dimension + 1):
           if record_1['var_' + str(i)] > record_2['var_' + str(i)]:
               is_1_dominated = False
               if is_2_dominated == False :
                   return 0
            
           elif record_2['var_' + str(i)] > record_1['var_' + str(i)]:
               is_2_dominated = False
               if is_1_dominated == False :
                   return 0
               

    if is_1_dominated == False and is_2_dominated == True : 
        return 1
    elif is_1_dominated == True and is_2_dominated == False : 
        return 2
    else:
        return 0
    
    
def compare_vectors(vector_1, vector_2, dimension, mcr_type):
    # mcr_type = 0(minimized), 1(maximized)
    # 0 = non domination, 1 = Record 1 dominates 2, 2 = 2 dominates 1
    is_1_dominated = True
    is_2_dominated = True
    
    if mcr_type == 0 :
        for i in range(dimension):
           if vector_1[i] < vector_2[i]:
               is_1_dominated = False
               if is_2_dominated == False :
                   return 0
            
           elif vector_2[i] < vector_1[i]:
               is_2_dominated = False
               if is_1_dominated == False :
                   return 0
               
    else:
        for i in range(dimension):
           if vector_1[i] > vector_2[i]:
               is_1_dominated = False
               if is_2_dominated == False :
                   return 0
            
           elif vector_2[i] > vector_1[i]:
               is_2_dominated = False
               if is_1_dominated == False :
                   return 0
               

    if is_1_dominated == False and is_2_dominated == True : 
        return 1
    elif is_1_dominated == True and is_2_dominated == False : 
        return 2
    else:
        return 0
    
    
    