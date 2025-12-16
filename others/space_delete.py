# This project rearrange a sentence by removing spaces and transform into a sentence without spaces.
def rearrange_sentence(sentence):
    new_sentence = ''
    for i in sentence:
        if i != ' ':
            new_sentence += i
    return new_sentence

input_sentence = []
inp=' '
while inp != '':
    inp = input()
    if inp != '':
        input_sentence.append(inp)
for i in range(len(input_sentence)):
    input_sentence[i] = rearrange_sentence(input_sentence[i])
output_sentence = ''.join(input_sentence)

print(output_sentence)  # Output: 东海上空经过哈理工