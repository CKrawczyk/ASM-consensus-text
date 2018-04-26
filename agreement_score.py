import pandas
import matplotlib.pyplot as plt
from scipy.stats import ks_2samp

colab = pandas.read_csv('ASM_5339_4_24_18.csv')
single = pandas.read_csv('ASM_5329_4_24_18.csv')


def agreement(reducer_table):
    consensus = []
    frames = sorted([c for c in reducer_table.columns if 'data.frame' in c])
    for idx, i in reducer_table.groupby('subject_id'):
        if i[i.reducer_key == 'complete']['data.0'].iloc[0] >= 5:
            reduction = i[i.reducer_key == 'ext'].iloc[0]
            for frame in frames:
                if not pandas.isnull(reduction[frame]):
                    data = eval(reduction[frame])
                    for line in data:
                        consensus.append(line['consensus_score'] / line['number_views'])
    return consensus


colab_agg = agreement(colab)
single_agg = agreement(single)

print(ks_2samp(colab_agg, single_agg))

plt.hist(colab_agg, bins=50, histtype='step', normed=True, cumulative=True, label='Colab')
plt.hist(single_agg, bins=50, histtype='step', normed=True, cumulative=True, label='Single')
plt.legend(loc=2)
plt.savefig('../agreement.png')
