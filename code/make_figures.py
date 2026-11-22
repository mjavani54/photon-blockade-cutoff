"""Create every manuscript figure from saved tables; no new cavity/QPU runs."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle, Arc

ROOT=Path(__file__).resolve().parents[1];D=ROOT/'data';F=ROOT/'figures'
F.mkdir(exist_ok=True)
C={'blue':'#245D8F','teal':'#008778','orange':'#D87B26','purple':'#8058A6','red':'#BE4547','ink':'#182B3A','grey':'#8694A0','light':'#E9EFF3'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.labelsize':9,'axes.titlesize':10,
 'legend.fontsize':7.5,'xtick.labelsize':8,'ytick.labelsize':8,'axes.spines.top':False,'axes.spines.right':False,
 'axes.linewidth':.7,'axes.edgecolor':'#6A7780','grid.color':'#D8DFE4','grid.linewidth':.5,
 'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none','savefig.facecolor':'white'})
def save(fig,name):
 for ext in ('png','pdf','svg'):fig.savefig(F/f'{name}.{ext}',dpi=400,bbox_inches='tight',pad_inches=.08)
 plt.close(fig)
def panel(ax,letter,title):
 ax.set_title(f'({letter})  {title}',loc='left',fontweight='bold',pad=9)
def table(name):return pd.read_csv(D/name)
def floor(x):return np.maximum(np.asarray(x,dtype=float),1e-18)
initial=pd.concat([table('initial_calibration_cases.csv'),table('initial_validation_cases.csv')],ignore_index=True)
two=initial[initial.group.str.startswith('two_')]
follow=table('followup_cases.csv');new=follow[follow.group.isin(['broad','polariton','strong_drive'])]
hardware=table('hardware_readout_results.csv')

def schematic():
 fig=plt.figure(figsize=(10,7.15));ax=fig.add_axes([0,0,1,1]);ax.set(xlim=(0,10),ylim=(0,7.15));ax.axis('off')
 def text(x,y,s,size=10,color=None,**kw):ax.text(x,y,s,fontsize=size,color=color or C['ink'],**kw)
 def arrow(a,b,color=C['ink'],lw=1.4,style='-|>'):
  ax.add_patch(FancyArrowPatch(a,b,arrowstyle=style,mutation_scale=11,color=color,lw=lw,shrinkA=3,shrinkB=3))
 def cavity(x,y,n):
  width=2.55;height=1.08
  ax.add_patch(FancyBboxPatch((x,y),width,height,boxstyle='round,pad=0.03,rounding_size=0.12',facecolor='#F1F7FB',edgecolor='none'))
  xx=np.linspace(x+.12,x+width-.12,400);wave=.22*np.sin((xx-x)*np.pi*3.9)
  ax.fill_between(xx,y+.53-wave,y+.53+wave,color='#A8CEDF',alpha=.42)
  ax.plot(xx,y+.53+wave,color=C['blue'],lw=1.1,alpha=.7)
  for xm in (x+.12,x+width-.12):
   ax.add_patch(Rectangle((xm-.045,y-.08),.09,height+.16,facecolor=C['blue'],edgecolor='none'))
   ax.add_patch(Rectangle((xm-.075,y-.08),.028,height+.16,facecolor='#A7B8C5',edgecolor='none'))
  xs=[x+width/2] if n==1 else [x+.9,x+1.7]
  for i,xm in enumerate(xs):
   ax.add_patch(Circle((xm,y+.53),.105,color=C['orange'],zorder=5))
   ax.add_patch(Circle((xm-.025,y+.565),.026,color='#FFE7BE',zorder=6))
   arrow((xm,y+.75),(xm+.1,y+1.12),C['red'],1)
   text(xm+.11,y+1.04,r'$\gamma_'+str(i+1)+'$',9,color=C['red'])
   text(xm,y+.16,r'$g_'+str(i+1)+'$',9,ha='center')
  arrow((x-.54,y+.52),(x+.02,y+.52),C['teal'],1.6);text(x-.28,y+.76,r'$\eta$',11,ha='center',color=C['teal'])
  arrow((x+width,y+.52),(x+width+.47,y+.52),C['blue'],1.6);text(x+width+.27,y+.77,r'$\kappa$',11,ha='center',color=C['blue'])
 text(.22,6.9,'(a)  Quantum cavity model and numerical transfer test',12,fontweight='bold')
 cavity(.9,5.38,1);cavity(6.08,5.38,2)
 text(2.16,5.08,'One emitter',11,ha='center',fontweight='bold');text(7.35,5.08,'Two emitters',11,ha='center',fontweight='bold')
 arrow((3.98,5.94),(5.48,5.94),C['purple'],1.8)
 text(4.72,6.29,'Frozen one emitter\ncalibration',9,ha='center',color=C['purple'])
 text(4.72,5.43,r'$\lambda = 1.64599$',10,ha='center',color=C['purple'])
 text(7.35,4.83,'Equal or unequal couplings and losses',8.5,ha='center',color=C['grey'])
 ax.plot([.2,9.8],[4.57,4.57],color='#D8E2E8',lw=.8)
 text(.22,4.27,'(b)  Cutoff and finite measurement planning',12,fontweight='bold')
 inset=fig.add_axes([.052,.385,.205,.175]);p=json.loads((D/'hardware_analysis_manifest.json').read_text())
 source=json.loads((D/'hardware_targets.json').read_text())['signal']['probabilities']
 inset.bar(np.arange(4),source,color=[C['blue'],C['teal'],C['orange'],C['purple']],width=.65)
 inset.set(xticks=range(4),xlabel='Photon number  n',ylabel=r'$p_n$',ylim=(0,.93));inset.tick_params(labelsize=7);inset.xaxis.label.set_size(8);inset.yaxis.label.set_size(9)
 inset.set_title('Stationary populations',fontsize=8,pad=5)
 arrow((2.85,3.37),(3.4,3.37),C['blue'])
 for x,w,title,body,color in ((3.53,2.56,'Choose photon cutoff',r'$m,\;m+1,\;m+2$'+'\nMoment weighted tail guard\nTarget scaled error  0.025',C['teal']),(6.91,2.58,'Choose measurement budget',r'$K_{00}+K_{11}+N_{\rm sci}$'+'\nDecision or precision goal\nFinite pilot uncertainty',C['purple'])):
  ax.add_patch(FancyBboxPatch((x,2.78),w,1.2,boxstyle='round,pad=0.09,rounding_size=.08',facecolor='white',edgecolor=color,lw=1.2))
  text(x+w/2,3.72,title,9.5,ha='center',fontweight='bold',color=color)
  text(x+w/2,3.24,body,8.5,ha='center',va='center',linespacing=1.55)
 arrow((6.18,3.37),(6.75,3.37),C['purple'])
 ax.plot([.2,9.8],[2.28,2.28],color='#D8E2E8',lw=.8)
 text(.22,1.99,'(c)  Processor experiment on prescribed number labels',12,fontweight='bold')
 text(.45,1.3,'Classical draw\n'+r'$n\sim p_n$'+'\n00  01  10  11',9,ha='center',va='center',linespacing=1.6)
 arrow((1.12,1.23),(1.7,1.23),C['blue'])
 for y,label,gate in ((1.56,r'$q_0$',r'$X^{b_0}$'),(.91,r'$q_1$',r'$X^{b_1}$')):
  text(1.77,y,label,8.5,va='center');ax.plot([2.28,4.4],[y,y],color=C['ink'],lw=1)
  ax.add_patch(Rectangle((2.56,y-.19),1.12,.38,fc='#E5F0F6',ec=C['blue'],lw=1))
  text(3.12,y,gate,9,ha='center',va='center')
  ax.add_patch(Rectangle((3.95,y-.2),.45,.4,fc='white',ec=C['ink'],lw=1))
  ax.add_patch(Arc((4.175,y-.02),.28,.22,theta1=0,theta2=180,color=C['ink']))
  ax.plot([4.175,4.275],[y-.02,y+.115],color=C['ink'],lw=1)
 arrow((4.55,1.23),(5.15,1.23),C['blue'])
 text(5.77,1.6,'Calibrate and infer',9,fontweight='bold',ha='center');text(5.77,1.18,'Basis calibration A\nand science counts',8.3,ha='center',va='center')
 arrow((6.42,1.23),(7.03,1.23),C['purple'])
 text(8.28,1.6,'Corrected moment interval',9,fontweight='bold',ha='center')
 ax.plot([7.41,9.27],[1.15,1.15],color=C['blue'],lw=2.5);ax.plot([7.41,7.41],[1.05,1.25],color=C['blue']);ax.plot([9.27,9.27],[1.05,1.25],color=C['blue']);ax.plot(8.22,1.15,'o',color=C['blue'],ms=5)
 text(8.3,.78,r'$g^{(2)}(0)$'+' from measured labels',9,ha='center')
 text(3.17,.51,r'$n=b_0+2b_1$',9,ha='center',color=C['grey'])
 text(5,.16,'Cavity dynamics are computed classically  |  Processor circuits test readout and allocation',9,ha='center',color=C['grey'])
 save(fig,'Fig01_experiment_schematic')

def initial_transfer():
 fig,axs=plt.subplots(1,2,figsize=(8.25,3.45),layout='constrained')
 traces=pd.concat([table('initial_calibration_cutoffs.csv'),table('initial_validation_cutoffs.csv')]);traces=traces.dropna(subset=['scaled_proposal_score'])
 lam=json.loads((D/'initial_rule.json').read_text())['proposal_multiplier']
 for group,label,color in [('one_calibration','One emitter calibration',C['blue']),('one_holdout','One emitter holdout',C['orange']),('two_identical','Two identical emitters',C['teal']),('two_mismatched','Two mismatched emitters',C['purple'])]:
  r=traces[traces.group==group]
  axs[0].scatter(floor(lam*(r.scaled_proposal_score+2e-6)),floor(r.scaled_error),s=5,alpha=.35,color=color,label=label,rasterized=True)
 axs[0].plot([1e-6,1e4],[1e-6,1e4],color=C['grey'],lw=.8,ls='--');axs[0].set(xscale='log',yscale='log',xlim=(1e-6,1e3),ylim=(1e-12,10),xlabel='Calibrated error proxy',ylabel='Actual scaled cutoff error');axs[0].legend(loc='lower right',markerscale=2,frameon=False)
 panel(axs[0],'a','Calibration and transfer at candidate cutoffs')
 for method,label,color in [('fixed3','Fixed cutoff 3',C['grey']),('boundary','Boundary probability',C['orange']),('difference','Adjacent change',C['purple']),('proposed','Moment aware',C['teal'])]:
  x=np.sort(np.maximum(two[method+'_scaled_error'],1e-12));axs[1].step(x,np.arange(1,len(x)+1)/len(x),where='post',label=label,color=color,lw=1.65)
 axs[1].axvline(.025,color=C['red'],ls='--',lw=1.2);axs[1].text(.029,.48,'Budget',color=C['red'],fontsize=8,rotation=90)
 axs[1].set(xscale='log',xlim=(1e-8,2),ylim=(0,1.025),xlabel='Selected cutoff scaled error',ylabel='Fraction of 240 two emitter cases');axs[1].legend(frameon=False,loc='upper left');panel(axs[1],'b','Selected cutoff error distributions')
 save(fig,'Fig02_initial_cutoff_transfer')

def guard():
 fig,ax=plt.subplots(1,2,figsize=(8.25,3.35),layout='constrained')
 for group,label,color in [('broad','Broad',C['blue']),('polariton','Polariton',C['teal']),('strong_drive','Strong drive',C['orange'])]:
  r=new[new.group==group];ax[0].scatter(floor(r.pilot_scaled_error),floor(r.guard_scaled_error),s=16,alpha=.8,label=label,color=color)
 ax[0].plot([1e-10,.1],[1e-10,.1],color=C['grey'],ls=':',lw=.8);ax[0].axvline(.025,color=C['red'],ls='--',lw=1);ax[0].axhline(.025,color=C['red'],ls='--',lw=1)
 ax[0].set(xscale='log',yscale='log',xlim=(1e-9,.08),ylim=(1e-9,.08),xlabel='Original rule scaled error',ylabel='Revised guard scaled error');ax[0].legend(frameon=False,loc='upper left');panel(ax[0],'a','New paired two emitter cases')
 xs=np.arange(3)
 for shift,key,label,color in [(-.18,'pilot_qubits','Original rule',C['grey']),(.18,'guard_qubits','Revised guard',C['teal'])]:
  counts=[int((new[key]==q).sum()) for q in (2,3,4)]
  bars=ax[1].bar(xs+shift,counts,width=.34,label=label,color=color)
  ax[1].bar_label(bars,padding=3,fontsize=8)
 ax[1].set(xticks=xs,xticklabels=['2 qubits','3 qubits','4 qubits'],ylabel='Number of new cases',ylim=(0,150));ax[1].legend(frameon=False);panel(ax[1],'b','Photon register cost of the guard')
 save(fig,'Fig03_guard_transfer_and_cost')

def verification():
 r=table('verification_reference_checks.csv');d=table('verification_independent_checks.csv')
 fig,ax=plt.subplots(1,2,figsize=(8.25,3.2),layout='constrained')
 r=r.sort_values('old_to_high_scaled_g2').reset_index(drop=True)
 for cohort,label,color in [('initial','Initial stress cases',C['orange']),('followup','All follow up records',C['blue'])]:
  pick=r.cohort==cohort;ax[0].scatter(np.flatnonzero(pick)+1,floor(r.loc[pick,'old_to_high_scaled_g2']),s=11,color=color,label=label)
 ax[0].axhline(2e-6,color=C['red'],ls='--',lw=1.1,label='Tolerance');ax[0].set(yscale='log',ylim=(1e-18,1e-5),xlabel='Reference case rank by correlation change',ylabel='Scaled change in reference correlation');ax[0].legend(frameon=False,loc='lower right');panel(ax[0],'a','Larger photon cutoff verification')
 x=np.arange(len(d));colors=[C['blue'] if m=='dense' else C['teal'] for m in d.method]
 ax[1].scatter(x,floor(d.scaled_g2_difference),c=colors,s=40);ax[1].axhline(2e-6,color=C['red'],ls='--',lw=1.1)
 labels=[k.replace('initial:','').replace('followup:','').replace('polariton-027-equal','P27 eq')+'\n'+('Dense' if m=='dense' else 'Time') for k,m in zip(d.case_key,d.method)]
 ax[1].set(yscale='log',ylim=(1e-18,1e-5),xticks=x,xticklabels=labels,ylabel='Scaled correlation difference');ax[1].tick_params(axis='x',labelsize=6.8);panel(ax[1],'b','Independent finite cutoff implementations')
 save(fig,'Fig04_numerical_verification')

def shots():
 a=new[new.reference_g2<1].copy();both=a[a.precision_shot_plan_pass&a.decision_shot_plan_pass]
 fig,ax=plt.subplots(1,2,figsize=(8.25,3.4),layout='constrained')
 for group,label,color in [('broad','Broad',C['blue']),('polariton','Polariton',C['teal'])]:
  rr=both[both.group==group];ax[0].scatter(rr.decision_shots_used,rr.precision_shots_used,s=25,color=color,label=label,alpha=.8)
 ax[0].plot([1e3,1e8],[1e3,1e8],ls='--',lw=.8,color=C['grey']);ax[0].set(xscale='log',yscale='log',xlim=(8e2,1.5e8),ylim=(8e2,1.5e8),xlabel='Decision goal shots',ylabel='Precision goal shots');ax[0].legend(frameon=False);panel(ax[0],'a','Both goals feasible in 36 cases')
 for feasible,marker,label in [(True,'o','Precision plan feasible'),(False,'v','Precision plan at cap')]:
  rr=a[a.precision_shot_plan_pass==feasible]
  ax[1].scatter(rr.pair_probability,rr.precision_shots_used,s=25,marker=marker,color=C['purple'] if feasible else C['orange'],label=label,alpha=.85)
 ax[1].set(xscale='log',yscale='log',xlabel=r'Pair probability  $\Pr(n\geq2)$',ylabel='Precision goal shots',ylim=(8e2,1.7e8));ax[1].legend(frameon=False,loc='lower left');panel(ax[1],'b','Rare pairs and finite shot budgets')
 save(fig,'Fig05_ideal_photon_shot_planning')

def allocation():
 a=table('allocation_plans.csv');a=a[a.scenario=='symmetric_0.02']
 cases=['polariton-027-equal','polariton-027-unequal','polariton-032-unequal','broad-015-unequal']
 policies=[('exact_rates','Exact rates',C['grey']),('fixed_100000','Fixed calibration',C['orange']),('optimized_equal','Equal optimized',C['blue']),('optimized_separate','Separate optimized',C['teal'])]
 fig,ax=plt.subplots(1,2,figsize=(8.25,3.6),layout='constrained')
 for axis,goal,letter in zip(ax,['decision','precision'],'ab'):
  for i,(key,label,color) in enumerate(policies):
   rr=a[(a.policy==key)&(a.goal==goal)].set_index('case_id').loc[cases]
   bars=axis.bar(np.arange(4)+(i-1.5)*.19,rr.total_shots,width=.18,color=color,label=label)
   for bar,status,total in zip(bars,rr.status,rr.total_shots):
    if pd.isna(total):
     axis.text(bar.get_x()+bar.get_width()/2,1.25e4,'NF',ha='center',va='bottom',fontsize=7,color=color,fontweight='bold')
    elif status!='planned':bar.set_hatch('///');bar.set_alpha(.35)
  axis.set(yscale='log',ylim=(1e4,4e8),xticks=range(4),xticklabels=['P27 equal','P27 unequal','P32 unequal','B15 unequal'],ylabel='Calibration plus signal shots');axis.tick_params(axis='x',rotation=24);panel(axis,letter,goal.capitalize()+' objective at 2 percent bit error')
 ax[0].legend(frameon=False,fontsize=7,loc='upper left');save(fig,'Fig06_joint_calibration_allocation')

def pilot():
 s=table('finite_pilot_summary.csv');s=s[(s.case_id=='polariton-027-equal')&(s.scenario=='symmetric_0.02')&(s.policy=='separate')]
 order=['small','medium','large'];x=[75000,370000,7200000]
 fig,ax=plt.subplots(1,2,figsize=(8.25,3.2),layout='constrained')
 for axis,goal,letter in zip(ax,['decision','precision'],'ab'):
  for method,label,color in [('plugin','Plug in',C['blue']),('robust','Robust pilot box',C['orange'])]:
   rr=s[(s.goal==goal)&(s.method==method)].set_index('pilot').loc[order]
   axis.plot(x,rr.goal_success_rate_all_pilots,'o-',color=color,lw=1.6,label=label)
   for xx,rate,success in zip(x,rr.goal_success_rate_all_pilots,rr.goal_successes):axis.annotate(f'{int(success)}/64',(xx,rate),textcoords='offset points',xytext=(0,-14 if method=='plugin' and rate>.8 else 8),ha='center',fontsize=7,color=color)
  axis.set(xscale='log',xticks=x,xticklabels=['75,000','370,000','7,200,000'],ylim=(-.08,1.08),xlabel='Total pilot shots',ylabel='End to end success fraction');axis.grid(axis='y');panel(axis,letter,goal.capitalize()+' from finite pilot data')
 ax[0].legend(frameon=False,loc='center right');save(fig,'Fig07_finite_pilot_planning')

def hardware_figure():
 fig,ax=plt.subplots(1,2,figsize=(8.25,3.45),layout='constrained')
 order=[('reference_allocation','signal'),('selected_allocation','signal'),('reference_allocation','control'),('selected_allocation','control')]
 labels=[]
 for y,(arm,pop) in enumerate(order):
  r=hardware[(hardware.arm==arm)&(hardware.population==pop)].iloc[0];color=C['blue'] if pop=='signal' else C['orange']
  ax[0].plot([r.interval_lower,r.interval_upper],[y,y],color=color,lw=2);ax[0].scatter(r.corrected_g2,y,s=26,color=color,zorder=3);ax[0].scatter(r.target_g2,y,marker='|',s=130,color=C['ink'],zorder=4)
  labels.append(('Reference' if arm.startswith('reference') else 'Selected')+' '+pop)
 ax[0].axvline(1,color=C['grey'],ls='--',lw=1);ax[0].set(yticks=range(4),yticklabels=labels,xlabel=r'Nominal label correlation  $g^{(2)}$',xlim=(.15,1.7));ax[0].invert_yaxis();panel(ax[0],'a','Observed simultaneous moment intervals')
 categories=[('Calibration',C['purple'],[99328,149504]),('Signal',C['blue'],[99328,111616]),('Control',C['orange'],[99328,36864]),('Excluded',C['light'],[6144,6144])]
 bottom=np.zeros(2)
 for label,color,values in categories:
  ax[1].bar(np.arange(2),values,bottom=bottom,color=color,label=label,width=.55,edgecolor='white',lw=.5);bottom+=values
 ax[1].set(xticks=[0,1],xticklabels=['Reference','Selected'],ylabel='Acquired shots per arm',ylim=(0,375000));ax[1].ticklabel_format(axis='y',style='sci',scilimits=(3,3));ax[1].legend(frameon=False,loc='upper center',ncol=2,fontsize=7);panel(ax[1],'b','Matched acquired budgets')
 save(fig,'FigS04_processor_readout_pilot')

def replication():
 d=table('replication_validation_case_comparison.csv');labels=['Stationary','Increasing','Decreasing','Pulse','High error','Persistent 01','Persistent 02']
 fig,ax=plt.subplots(1,2,figsize=(8.25,3.35),layout='constrained');y=np.arange(len(d))
 ax[0].scatter(d.reference_joint_success,y,color=C['orange'],label='Reference point rate',s=23)
 ax[0].scatter(d.selected_joint_success,y,color=C['blue'],label='Selected point rate',s=23)
 for i,r in d.iterrows():ax[0].plot([r.selected_joint_lower_bound,r.selected_joint_success],[i,i],color=C['blue'],lw=1.3)
 ax[0].set(yticks=y,yticklabels=labels,xlim=(.25,1.035),xlabel='Simulated joint success probability');ax[0].invert_yaxis();ax[0].legend(frameon=False,loc='lower left',fontsize=7);panel(ax[0],'a','Independent matched model validation')
 ax[1].barh(y,d.future64_comparison_power_lower_bound,color=C['teal'],height=.58)
 ax[1].axvline(.8,color=C['red'],ls='--',lw=1.1);ax[1].set(yticks=y,yticklabels=[],xlim=(.75,1.015),xlabel='Lower bound on 64 pair comparison power');ax[1].invert_yaxis();panel(ax[1],'b','Prospective series remains uncollected')
 fig.text(.61,-.02,'512 proposed jobs; 130.6 estimated RUs',fontsize=8,color=C['grey'],ha='center')
 save(fig,'FigS05_prospective_replication_models')

def supplement():
 t=table('initial_validation_cutoffs.csv');fig,ax=plt.subplots(1,2,figsize=(8.25,3.1),layout='constrained')
 for axis,cid,letter in zip(ax,['S037','M037'],'ab'):
  r=t[t.case_id==cid].sort_values('cutoff');ref=initial[initial.case_id==cid].iloc[0].reference_g2
  axis.plot(r.cutoff,r.g2,'o-',color=C['blue'],ms=3,label='Finite cutoff');axis.axhline(ref,color=C['ink'],lw=.9,label='Reference')
  axis.axhspan(ref/1.025,ref/.975,color=C['teal'],alpha=.1,label='Scaled error budget');axis.axvline(7,color=C['orange'],ls='--',lw=1,label='Original choice');axis.axvline(8,color=C['purple'],ls=':',lw=1.2,label='Guard choice')
  axis.set(xlabel='Maximum retained photon number',ylabel=r'$g^{(2)}(0)$',xlim=(2,16),ylim=(1.4,2.05));panel(axis,letter,cid+' known miss diagnostic')
 ax[0].legend(frameon=False,fontsize=7,loc='lower right');save(fig,'FigS01_known_miss_cutoff_paths')
 s=table('finite_pilot_summary.csv');s=s[s.policy=='separate'];cases=['polariton-027-equal','polariton-027-unequal','polariton-032-unequal','broad-015-unequal'];scenarios=list(s.scenario.unique())
 fig,axes=plt.subplots(2,2,figsize=(8.25,5.6),layout='constrained')
 for axis,(method,goal),letter in zip(axes.ravel(),[(m,g) for m in ['plugin','robust'] for g in ['decision','precision']],'abcd'):
  rows=[]
  for pilot in ['small','medium','large']:
   for cid in cases:
    rr=s[(s.method==method)&(s.goal==goal)&(s.pilot==pilot)&(s.case_id==cid)].set_index('scenario').loc[scenarios];rows.append(rr.goal_success_rate_all_pilots.to_numpy())
  matrix=np.asarray(rows);im=axis.imshow(matrix,aspect='auto',vmin=0,vmax=1,cmap='YlGnBu')
  axis.set(xticks=range(6),xticklabels=['0.5%','1%','2%','3%','5%','Asym'],yticks=range(12),yticklabels=[p+' '+c for p in ['S','M','L'] for c in ['P27e','P27u','P32u','B15u']]);axis.tick_params(labelsize=6.8)
  for cut in [3.5,7.5]:axis.axhline(cut,color='white',lw=1.5)
  panel(axis,letter,method.capitalize()+' '+goal)
 fig.colorbar(im,ax=axes,shrink=.7,label='End to end success fraction');save(fig,'FigS02_all_finite_pilot_conditions')
 c=table('hardware_calibration_and_heldout.csv');fig,ax=plt.subplots(1,2,figsize=(7.8,3.25),layout='constrained')
 for axis,arm,letter in zip(ax,['reference_allocation','selected_allocation'],'ab'):
  r=c[c.arm==arm];matrix=np.empty((4,4))
  for _,row in r.iterrows():
   obs=int(str(row.observed_state),2) if isinstance(row.observed_state,str) else int(str(int(row.observed_state)),2)
   prep=int(str(row.prepared_state),2) if isinstance(row.prepared_state,str) else int(str(int(row.prepared_state)),2)
   matrix[obs,prep]=row.assignment_estimate
  im=axis.imshow(matrix,vmin=0,vmax=1,cmap='Blues')
  for i in range(4):
   for j in range(4):axis.text(j,i,f'{matrix[i,j]:.3f}',ha='center',va='center',fontsize=8,color='white' if matrix[i,j]>.6 else C['ink'])
  axis.set(xticks=range(4),yticks=range(4),xticklabels=['00','01','10','11'],yticklabels=['00','01','10','11'],xlabel='Prepared label',ylabel='Observed label');panel(axis,letter,arm.split('_')[0].capitalize()+' assignment estimate')
 fig.colorbar(im,ax=ax,shrink=.8,label='Observed conditional frequency');save(fig,'FigS03_measured_assignment_matrices')

if __name__=='__main__':
 for function in (schematic,initial_transfer,guard,verification,shots,allocation,pilot,hardware_figure,replication,supplement):function()
 print('Created seven main figures and five supplementary figures in PNG PDF and SVG formats')
