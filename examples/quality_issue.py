def process(numbers):
    result = []
    for i in range(len(numbers)):
        if numbers[i] % 2 == 0:
            result.append(numbers[i] * 2)
    return result

data = [1, 2, 3, 4, 5, 6]
print(process(data))
