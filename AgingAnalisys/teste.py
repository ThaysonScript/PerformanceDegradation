if highlighted_subdatasets:
        fig, ax = plt.subplots(figsize=(15, 10))
        for process, subset in highlighted_subdatasets.items():
            subset['time_in_hours'] = (subset['datetime'] - subset['datetime'].min()).dt.total_seconds() / 3600
            ax.step(subset['time_in_hours'], subset['process_occurrences'], where='post', label=f'{process}', linewidth=3)

        # ax.legend(loc='best', fontsize='small', title='Process')
        ax.legend(loc='best', fontsize='small', ncol=2, frameon=True, framealpha=0.9, edgecolor='black', title='Process')
        ax.set_xlabel('Time (hours)')
        ax.set_ylabel('Process occurrences', labelpad=15)

        if adjust_x_limits:
            max_time = max(
                (subset['datetime'].max() - subset['datetime'].min()).total_seconds() / 3600
                for subset in highlighted_subdatasets.values()
            )
            ax.set_xlim([0, max_time])

        for spine in ax.spines.values():
            spine.set_linewidth(1.5)

        plt.tight_layout()
        plt.savefig(f"imagens_plottadas/time_series_memory_fragmentation_Process_{i * process_per_plot + 1}_{(i + 1) * process_per_plot}.svg", bbox_inches='tight', dpi=300, format="svg")
        plt.close(fig)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
# ax.legend(loc='best', fontsize='small', title='Process', ncol=2)
ax.legend(loc='best', fontsize='small', ncol=2, frameon=True, framealpha=0.9, edgecolor='black', title='Process')
ax.set_xlabel('Time (hours)')
ax.set_ylabel('Process occurrences', labelpad=15)

if adjust_x_limits:
    ax.set_xlim([0, max_time])

for spine in ax.spines.values():
    spine.set_linewidth(1.5)

plt.tight_layout()
plt.savefig(f"imagens_plottadas/time_series_memory_fragmentation_Process_{i * process_per_plot + 1}_{(i + 1) * process_per_plot}.svg", bbox_inches='tight', dpi=300, format="svg")
plt.close(fig)