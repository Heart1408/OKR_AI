import os
import wget

file_links = [
    {
        'title': 'Attention Is All You Need',
        'url': 'https://arxiv.org/pdf/2312.16862',
    },
    {
        'title': 'BERT- Pre-training of Deep Bidirectional Transformers for Language Understanding',
        'url': 'https://arxiv.org/pdf/1810.04805',
    },
    {
        'title': 'Instruction Tuning for Large Language Models- A Survey',
        'url': 'https://arxiv.org/pdf/2308.10792',
    },
    {
        'title': 'Language Models are Few-Shot Learners',
        'url': 'https://arxiv.org/pdf/2005.14165',
    },
    {
        'title': 'THE PRODUCT OF LATTICE COVOLUME AND DISCRETE SERIES FORMAL DIMENSION',
        'url': 'https://arxiv.org/pdf/1901.11501',
    },
    {
        'title': 'Prompt Programming for Large Language Models- Beyond the Few-Shot Paradigm',
        'url': 'https://arxiv.org/pdf/2102.07350',
    }
]

def is_exist(file_link):
    return os.path.exists(f"./{file_link['title']}.pdf")

for file_link in file_links:
    if not is_exist(file_link):
        wget.download(file_link['url'], out=f"./{file_link['title']}.pdf")
