import my_llm
while True:
    request = input("Введите запрос, или end для выхода:  ")
    if request == "end":
        break
    llm_inv = my_llm.llm_invoke(request)
    print (llm_inv)

