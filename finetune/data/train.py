import json
import os

import shortuuid


def load_math_folder(data_folder):
    results = []
    for filename in os.listdir(data_folder):
        if filename.endswith(".jsonl"):
            file_path = os.path.join(data_folder, filename)
            curr_result = load_math_data(file_path)
            print(filename, len(curr_result))
            results.extend(curr_result)
    return results


def load_math_data(data_file):
    result = []
    with open(data_file, 'r') as f:
        for line in f:
            labeled_solution = json.loads(line.strip())
            problem = labeled_solution['question']['problem']
            answer = labeled_solution['question']['ground_truth_answer']

            completions = [{"text": step["human_completion"]['text'], "rating": 1}
                           if step["chosen_completion"] is None else
                           {"text": step["completions"][step["chosen_completion"]]["text"],
                            "rating": step["completions"][step["chosen_completion"]]['rating']}
                           for step in labeled_solution["label"]["steps"]
                           if step['human_completion'] is not None or step['chosen_completion'] is not None]

            # completions.append({"text": "# Answer\n\n%s" % answer, "rating": 1})
            result.append({"problem": problem, "answer": answer, "completions": completions})
    
    return result



def convert(old):
    new = []
    for item in old:
        problem = item['problem']
        answer = item['answer']
        completions = item['completions']
        conv = [{
            "from": "human",
            "value": problem
        }]
        for comp in completions:
            conv.append({
                "from": "gpt",
                "value": comp['text']
            })
            conv.append({
                "from": "human",
                "value": "This step is appropriate in context, reasonable, correct, contains easily verifiable computations, and also progresses towards the solution."
            })
        conv.append({
            "from": "gpt",
            "value": answer
        })
        new.append({
                'id': shortuuid.uuid(),
                'conversations': conv
        })
    
    return new


if __name__ == '__main__':
    data = load_math_folder('../prm800k/data')
    new_data = convert(data)
    print(len(new_data))
    with open('prm800k_vicuna_format.jsonl', 'w') as g:
        json.dump(new_data, g)
    