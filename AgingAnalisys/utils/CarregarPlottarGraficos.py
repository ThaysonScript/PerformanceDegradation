import sys
from classes.PlottarFragmentado import PlottarFragmentado
from classes.PlottarGraficos import PlottarGraficos
from classes.OtherPlots import plot, plot_fragmentation
from utils.TratamentoErrosEnvelhecimentoLogs import TratamentoErrosEnvelhecimentoLogs
from utils.Logs import Logs


class CarregarPlottarGraficos():
    def __init__(self, tipo_virtualizador):
        self.virtualizador = tipo_virtualizador
        
        
    def _common_ylabels(self):
        return {
            'cpu': 'CPU Utilization (\\%)',
            'mem': 'Memory Usage (\\%)',
            'rss': 'Physical Memory (MB)',
            'vsz': 'Virtual Memory (MB)',
            'threads': 'Thread Count',
            'swap': 'Swap Usage (MB)'
        }
        
    
    def _common_cpu_labels(self):
        return {
            '%usr': 'User CPU Usage (\\%)',
            '%nice': 'Nice CPU Usage (\\%)',
            '%sys': 'System CPU Usage (\\%)',
            '%iowait': 'I/O Wait CPU Usage (\\%)',
            '%soft': 'Soft CPU Usage (\\%)'
        }
    
    
    # ------------------------------------------------ VIRTUALIZADORES ------------------------------------------- #
    def vbox_plotttar(self):
        # PlottarGraficos().plottar(
        #     title="JMETER",
        #     filename=jmeter['jmeter_log'],
        #     ylabel='(none)',
        #     dayfirst=True, includeColYlabel=True
        # )
        
        vbox = Logs(self.virtualizador)
        TratamentoErrosEnvelhecimentoLogs(pasta_logs=vbox.vboxMonitoringFolder, barras=True, ponto=True)

        # PlottarFragmentado().analisar(arquivo=vbox.vboxLogs['fragmentation'])
        plot_fragmentation(vbox.vboxMonitoringFolder, merge_equals=True, exclude_names=['ps'])
                
        PlottarGraficos().plottar(
            title="vbox_CPU_Utilization_Across_All_Cores_Over_Time", 
            nomeArquivo=vbox.vboxLogs['cpu_sum_all_cores'], 
            cols_to_divide=[
                '%usr', '%nice', '%sys', '%iowait', '%soft',
            ],
            ylabel={
                **self._common_cpu_labels()
            },
            dayfirst=True,
            apply_mann_kendall=True
        )
        
        PlottarGraficos().plottar(
            title="vbox_Average_CPU_Utilization_Across_All_Cores_Over_Time",
            nomeArquivo=vbox.vboxLogs['monitoring_cpu'], 
            ylabel='Average Cpu Utilization (\\%)', 
            dayfirst=True, 
            # includeColYlabel=True,
            apply_mann_kendall=True
        )

        PlottarGraficos().plottar(
            title="vbox_Disk_Usage_Over_Time", 
            nomeArquivo=vbox.vboxLogs['monitoring_disks'], 
            ylabel='Disk Usage (GB)', 
            dayfirst=True, division=(1024**2),
            apply_mann_kendall=True
        )

        PlottarGraficos().plottar(
            title="vbox_Number_Zombie_Processes_Over_Time", 
            nomeArquivo=vbox.vboxLogs['monitoring_zumbies'], 
            ylabel='Number of Zombie Processes', 
            dayfirst=True,
            resample_method='max',
            apply_mann_kendall=True
        )

        PlottarGraficos().plottar(
            title="vbox_Memory_Usage_Over_Time", 
            nomeArquivo=vbox.vboxLogs['monitoring_mem'], 
            ylabel='Memory Usage (MB)', 
            dayfirst=True, 
            division=1024, 
            # includeColYlabel=True,
            apply_mann_kendall=True
        )

        PlottarGraficos().plottar(
            title="vbox_Process_VBoxHeadless", 
            nomeArquivo=vbox.vboxLogs['monitoring_VboxHeadless'], 
            cols_to_divide=["rss","vsz", "swap"],
            ylabel={
                **self._common_ylabels()
            },
            division=1024, dayfirst=True,
            apply_mann_kendall=True
        )

        PlottarGraficos().plottar(
            title="vbox_Process_VBoxSVC", 
            nomeArquivo=vbox.vboxLogs['monitoring_VboxSvc'], 
            cols_to_divide=["rss","vsz","swap"],
            ylabel={
                **self._common_ylabels()
            },
            division=1024, dayfirst=True,
            apply_mann_kendall=True
        )

        PlottarGraficos().plottar(
            title="vbox_Process_VBoxXPCOMIPCD", 
            nomeArquivo=vbox.vboxLogs['monitoring_VboxXPCOMIPCD'], 
            cols_to_divide=["rss", "vsz", "swap"],
            ylabel={
                **self._common_ylabels()
            },
            division=1024, dayfirst=True,
            apply_mann_kendall=True
        )

        PlottarGraficos().plottar(
            title="vbox_Nginx_Server_Response_Time_Over_Time", 
            nomeArquivo=vbox.vboxLogs['server_response_time_monitoring'], 
            ylabel='Response Time (milliseconds)', 
            multiply=1000, dayfirst=True,
            apply_mann_kendall=True
        )
        
        
    def kvm_plottar(self):   
        kvm = Logs(self.virtualizador)
        # fragmentacao(MINIMUM_PROCESS_OCCURRENCES)
        # PlottarGraficos().plottar_fragmentation(PASTA_LOGS)
        # PlottarFragmentado().analisar(arquivo=kvm.kvmLogs['fragmentation'])
        # cut_data = '16-12-2024-14:11:30'
        cut_data = 348
        
        plot_fragmentation(kvm.kvmMonitoringFolder, merge_equals=True, cut_dataset='Mon Dec 16 17:12:49 2024', exclude_names=['find', 'ps', 'bash'])
        
        # sys.exit(1)
        PlottarGraficos().plottar(
            title="kvm_CPU_Utilization_Across_All_Cores_Over_Time", 
            nomeArquivo=kvm.kvmLogs['cpu_sum_all_cores'], 
            cols_to_divide=[
                '%usr', '%nice', '%sys', '%iowait', '%soft',
            ],
            ylabel={
                **self._common_cpu_labels()
            },
            dayfirst=True,
            cut_dataset=cut_data,
            apply_mann_kendall=True
        )
        
        PlottarGraficos().plottar(
            title="kvm_Average_CPU_Utilization_Across_All_Cores_Over_Time",
            nomeArquivo=kvm.kvmLogs['monitoring_cpu'], 
            ylabel='Average Cpu Utilization (\\%)', 
            dayfirst=True, 
            # includeColYlabel=True,
            cut_dataset=cut_data,
            apply_mann_kendall=True
        )

        PlottarGraficos().plottar(
            title="kvm_Disk_Usage_Over_Time", 
            nomeArquivo=kvm.kvmLogs['monitoring_disks'], 
            ylabel='Disk Usage (GB)', 
            dayfirst=True, division=(1024**2),
            cut_dataset=cut_data,
            apply_mann_kendall=True
        )

        PlottarGraficos().plottar(
            title="kvm_Number_Zombie_Processes_Over_Time", 
            nomeArquivo=kvm.kvmLogs['monitoring_zumbies'], 
            ylabel='Number of Zombie Processes', 
            dayfirst=True,
            cut_dataset=cut_data,
            resample_method='max',
            apply_mann_kendall=True
        )


        PlottarGraficos().plottar(
            title="kvm_Memory_Usage_Over_Time", 
            nomeArquivo=kvm.kvmLogs['monitoring_mem'], 
            ylabel='Memory Usage (MB)', 
            dayfirst=True, 
            division=1000,
            # includeColYlabel=True,
            cut_dataset=cut_data,
            apply_mann_kendall=True
        )
        
        PlottarGraficos().plottar(
            title="kvm_Process_kvmHeadless", 
            nomeArquivo=kvm.kvmLogs['kvm_Headless'], 
            cols_to_divide=["rss","vsz","swap"],
            ylabel={
                **self._common_ylabels()
            },
            division=1024, dayfirst=True,
            cut_dataset=cut_data,
            apply_mann_kendall=True
        )

        PlottarGraficos().plottar(
            title="kvm_Process_kvm_libvirt_service", 
            nomeArquivo=kvm.kvmLogs['kvm_libvirtd_service'], 
            cols_to_divide=["vsz", 'rss', "swap"],
            ylabel={
                'cpu': 'CPU Utilization (\\%)',
                'mem': 'Memory Usage (\\%)',
                'vsz': 'Virtual Memory (MB)',
                'rss': 'Physical Memory (MB)',
                'threads': 'Thread Count',
                'swap': 'Swap Usage (MB)'
            },
            division=1024, dayfirst=True,
            cut_dataset=cut_data,
            apply_mann_kendall=True
        )
    
        PlottarGraficos().plottar(
            title="kvm_Nginx_Server_Response_Time_Over_Time", 
            nomeArquivo=kvm.kvmLogs['server_response_time_monitoring'], 
            ylabel='Response Time (milliseconds)', 
            multiply=1000, dayfirst=True,
            cut_dataset=cut_data,
            apply_mann_kendall=True
        )


    def xen_plottar(self):
        xen = Logs(self.virtualizador)
        # fragmentacao(MINIMUM_PROCESS_OCCURRENCES)
        # PlottarGraficos().plottar_fragmentation(PASTA_LOGS)
        plot_fragmentation(xen.xenMonitoringFolder, merge_equals=True, exclude_names=['xen-balloon_mon', 'find', 'awk', 'bash', 'xenstored_monit', 'ps', 'xenconsoled_mon', 'xl'])
        
        cut_data = 348
        
        PlottarGraficos().plottar(
            title="xen_CPU_Utilization_Across_All_Cores_Over_Time", 
            nomeArquivo=xen.xenLogs['cpu_sum_all_cores'], 
            cols_to_divide=[
                '%usr', '%nice', '%sys', '%iowait', '%soft',
            ],
            ylabel={
                **self._common_cpu_labels()
            },
            dayfirst=True,
            apply_mann_kendall=True,
            cut_dataset=cut_data
        )        
        
        PlottarGraficos().plottar(
            title="xen_Average_CPU_Utilization_Across_All_Cores_Over_Time",
            nomeArquivo=xen.xenLogs['monitoring_cpu'], 
            ylabel='Average CPU Utilization (\\%)', 
            dayfirst=True, 
            # includeColYlabel=True
            apply_mann_kendall=True,
            cut_dataset=cut_data
        )

        PlottarGraficos().plottar(
            title="xen_Disk_Usage_Over_Time", 
            nomeArquivo=xen.xenLogs['monitoring_disks'], 
            ylabel='Disk Usage (GB)', 
            dayfirst=True, division=(1024**2),
            apply_mann_kendall=True,
            cut_dataset=cut_data
        )

        PlottarGraficos().plottar(
            title="xen_Number_Zombie_Processes_Over_Time", 
            nomeArquivo=xen.xenLogs['monitoring_zumbies'], 
            ylabel='Number of Zombie Processes', 
            dayfirst=True,
            apply_mann_kendall=True,
            resample_method='max',
            cut_dataset=cut_data
        )

        PlottarGraficos().plottar(
            title="xen_Memory_Usage_Over_Time", 
            nomeArquivo=xen.xenLogs['monitoring_mem'], 
            ylabel='Memory Usage (MB)', 
            dayfirst=True, 
            division=1024, 
            # includeColYlabel=True,
            apply_mann_kendall=True,
            cut_dataset=cut_data
        )

        
        PlottarGraficos().plottar(
            title="xen_Process_xen_monitoring_oxenstored", 
            nomeArquivo=xen.xenLogs['xen_monitoring_oxenstored'], 
            cols_to_divide=["rss","vsz","swap"],
            ylabel={
                **self._common_ylabels()
            },
            division=1024, dayfirst=True,
            apply_mann_kendall=True,
            cut_dataset=cut_data
        )

        PlottarGraficos().plottar(
            title="xen_Process_xen_monitoring_xen_balloon", 
            nomeArquivo=xen.xenLogs['xen_monitoring_xen_balloon'], 
            cols_to_divide=["rss","vsz","swap"],
            ylabel={
                **self._common_ylabels()
            },
            division=1024, dayfirst=True,
            apply_mann_kendall=True,
            cut_dataset=cut_data
        )
        
        PlottarGraficos().plottar(
            title="xen_Process_xen_monitoring_xenbus", 
            nomeArquivo=xen.xenLogs['xen_monitoring_xenbus'], 
            cols_to_divide=["rss","vsz","swap"],
            ylabel={
                **self._common_ylabels()
            },
            division=1024, dayfirst=True,
            apply_mann_kendall=True,
            cut_dataset=cut_data
        )

        PlottarGraficos().plottar(
            title="xen_Process_xen_monitoring_xenconsoled", 
            nomeArquivo=xen.xenLogs['xen_monitoring_xenconsoled'], 
            cols_to_divide=["rss","vsz","swap"],
            ylabel={
                **self._common_ylabels()
            },
            division=1024, dayfirst=True,
            apply_mann_kendall=True,
            cut_dataset=cut_data
        )

        PlottarGraficos().plottar(
            title="xen_Nginx_Server_Response_Time_Over_Time", 
            nomeArquivo=xen.xenLogs['server_response_time_monitoring'], 
            ylabel='Response Time (milliseconds)', 
            multiply=1000, dayfirst=True,
            apply_mann_kendall=True,
            cut_dataset=cut_data
        )


    def lxd_plottar(self):
        lxd = Logs(self.virtualizador)
        # fragmentacao(MINIMUM_PROCESS_OCCURRENCES)
        # PlottarGraficos().plottar_fragmentation(PASTA_LOGS)
        # PlottarFragmentado().analisar(arquivo=lxd.lxdLogs['fragmentation'])
        
        plot_fragmentation(lxd.lxdMonitoringFolder, merge_equals=True, exclude_names=['bash', 'pgrep'])
        
        cut_data = 348
        
        PlottarGraficos().plottar(
            title="lxd_CPU_Utilization_Across_All_Cores_Over_Time", 
            nomeArquivo=lxd.lxdLogs['cpu_sum_all_cores'], 
            cols_to_divide=[
                '%usr', '%nice', '%sys', '%iowait', '%soft',
            ],
            ylabel={
                **self._common_cpu_labels()
            },
            dayfirst=True,
            apply_mann_kendall=True,
            cut_dataset=cut_data
        )
        
        PlottarGraficos().plottar(
            title="lxd_Average_CPU_Utilization_Across_All_Cores_Over_Time",
            nomeArquivo=lxd.lxdLogs['monitoring_cpu'], 
            ylabel='Average Cpu Utilization (\\%)', 
            dayfirst=True, 
            # includeColYlabel=True,
            apply_mann_kendall=True,
            cut_dataset=cut_data
        )

        PlottarGraficos().plottar(
            title="lxd_Disk_Usage_Over_Time", 
            nomeArquivo=lxd.lxdLogs['monitoring_disks'], 
            ylabel='Disk Usage (GB)', 
            dayfirst=True, division=(1024**2),
            apply_mann_kendall=True,
            cut_dataset=cut_data
        )
        
        PlottarGraficos().plottar(
            title="lxd_Number_Zombie_Processes_Over_Time", 
            nomeArquivo=lxd.lxdLogs['monitoring_zumbies'], 
            ylabel='Number of Zombie Processes', 
            dayfirst=True,
            apply_mann_kendall=True,
            multiply=1,
            resample_method='max',
            cut_dataset=cut_data
        )


        PlottarGraficos().plottar(
            title="lxd_Memory_Usage_Over_Time", 
            nomeArquivo=lxd.lxdLogs['monitoring_mem'], 
            ylabel='Memory Usage (MB)', 
            dayfirst=True, 
            division=1000,
            # includeColYlabel=True,
            apply_mann_kendall=True,
            cut_dataset=cut_data
        )
        
        PlottarGraficos().plottar(
            title="lxd_Process_lxdHeadless", 
            nomeArquivo=lxd.lxdLogs['lxd_vm_qemu_process'], 
            cols_to_divide=["rss","vsz","swap"],
            ylabel={
                **self._common_ylabels()
            },
            division=1024, dayfirst=True,
            apply_mann_kendall=True,
            cut_dataset=cut_data
        )

        PlottarGraficos().plottar(
            title="lxd_Process_lxd_group_process_monitoring", 
            nomeArquivo=lxd.lxdLogs['lxd_group_process_monitoring'], 
            cols_to_divide=["vsz", 'rss', "swap"],
            ylabel={
                **self._common_ylabels()
            },
            division=1024, dayfirst=True,
            apply_mann_kendall=True,
            cut_dataset=cut_data
        )
    
        PlottarGraficos().plottar(
            title="lxd_Nginx_Server_Response_Time_Over_Time", 
            nomeArquivo=lxd.lxdLogs['server_response_time_monitoring'], 
            ylabel='Response Time (milliseconds)', 
            multiply=1000, dayfirst=True,
            apply_mann_kendall=True,
            cut_dataset=cut_data
        )


    # ------------------------------------------------ CONTAINERS ------------------------------------------- #
    def docker_antigo(self):
        dock_antigo = Logs()
        # fragmentacao(MINIMUM_PROCESS_OCCURRENCES)
        # PlottarGraficos().plottar_fragmentation(PASTA_LOGS)
        
        # sys.exit(0)    
        # PlottarGraficos().plottar(
        #     title="runs",
        #     filename=dock_novo['runs'], 
        #     ylabel='(percentage)', 
        #     dayfirst=True, includeColYlabel=True
        # )
        
        # --------------------- MACHINE RESOURCES
        PlottarGraficos().plottar(
            title="CPU",
            filename=dock_antigo['cpu'], 
            ylabel='(percentage)', 
            dayfirst=True, includeColYlabel=True
        )

        PlottarGraficos().plottar(
            title="Memory Usage Over Time", 
            filename=dock_antigo['memory'], 
            ylabel='Memory Usage (MB)', 
            dayfirst=True, 
            division=1024, includeColYlabel=True
        )
        
        PlottarGraficos().plottar(
            title="Disk Usage Over Time", 
            filename=dock_antigo['disk'], 
            ylabel='Disk usage (GB)', 
            dayfirst=True, division=(1024**2)
        )

        PlottarGraficos().plottar(
            title="Zumbis", 
            filename=dock_antigo['process'], 
            ylabel='Zumbis processes(qtt)', 
            dayfirst=True
        )

        # -------------------------- CONTAINER PROCESS
        PlottarGraficos().plottar(
            title="nginx",
            filename=dock_antigo['nginx'], 
            ylabel='(seconds)', 
            dayfirst=True, includeColYlabel=True,
            division=1e+9
        )
        
        # PlottarGraficos().plottar(
        #     title="postgres",
        #     filename=dock_antigo['postgres'], 
        #     ylabel='(seconds)', 
        #     dayfirst=True, includeColYlabel=True,
        #     division=1e+9
        # )
        
        PlottarGraficos().plottar(
            title="rabbitmq",
            filename=dock_antigo['rabbitmq'], 
            ylabel='(seconds)', 
            dayfirst=True, includeColYlabel=True,
            division=1e+9
        )
        
        PlottarGraficos().plottar(
            title="redis",
            filename=dock_antigo['redis'], 
            ylabel='(seconds)', 
            dayfirst=True, includeColYlabel=True,
            division=1e+9
        )
        
        # ----------------------------- DOCKER PROCESS
        PlottarGraficos().plottar(
            title="docker_antigo - process",
            filename=dock_antigo['docker'], 
            ylabel={
                'cpu': 'CPU usage (percentage)',
                'mem': 'Memory usage (percentage)',
                'rss': 'Physical memory usage(MB)',
                'vsz': 'Virtual memory usage (MB)',
                'threads': 'Number of threads(qtt)',
                'swap': 'Swap used(MB)',
            },
            dayfirst=True, includeColYlabel=True,
            cols_to_divide=['rss', 'vsz', 'swap'],
            division=1024
        )
        
        PlottarGraficos().plottar(
            title="dockerd_antigo - process",
            filename=dock_antigo['dockerd'], 
            ylabel={
                'cpu': 'CPU usage (percentage)',
                'mem': 'Memory usage (percentage)',
                'rss': 'Physical memory usage(MB)',
                'vsz': 'Virtual memory usage (MB)',
                'threads': 'Number of threads(qtt)',
                'swap': 'Swap used(MB)',
            },
            dayfirst=True, includeColYlabel=True,
            cols_to_divide=['rss', 'vsz', 'swap'],
            division=1024
        )
        
        PlottarGraficos().plottar(
            title="containerd_antigo - process",
            filename=dock_antigo['containerd'], 
            ylabel={
                'cpu': 'CPU usage (percentage)',
                'mem': 'Memory usage (percentage)',
                'rss': 'Physical memory usage(MB)',
                'vsz': 'Virtual memory usage (MB)',
                'threads': 'Number of threads(qtt)',
                'swap': 'Swap used(MB)',
            },
            dayfirst=True, includeColYlabel=True,
            cols_to_divide=['rss', 'vsz', 'swap'],
            division=1024
        )
        
        PlottarGraficos().plottar(
            title="containerd-shim_antigo - process",
            filename=dock_antigo['containerd-shim'], 
            ylabel={
                'cpu': 'CPU usage (percentage)',
                'mem': 'Memory usage (percentage)',
                'rss': 'Physical memory usage(MB)',
                'vsz': 'Virtual memory usage (MB)',
                'threads': 'Number of threads(qtt)',
                'swap': 'Swap used(MB)',
            },
            dayfirst=True, includeColYlabel=True,
            cols_to_divide=['rss', 'vsz', 'swap'],
            division=1024
        )
        
        PlottarGraficos().plottar(
            title="docker-proxy_antigo - process",
            filename=dock_antigo['docker-proxy'], 
            ylabel={
                'cpu': 'CPU usage (percentage)',
                'mem': 'Memory usage (percentage)',
                'rss': 'Physical memory usage(MB)',
                'vsz': 'Virtual memory usage (MB)',
                'threads': 'Number of threads(qtt)',
                'swap': 'Swap used(MB)',
            },
            dayfirst=True, includeColYlabel=True,
            cols_to_divide=['rss', 'vsz', 'swap'],
            division=1024
        )
        
        PlottarGraficos().plottar(
            title="runc_novo - process",
            filename=dock_antigo['runc'], 
            ylabel={
                'cpu': 'CPU usage (percentage)',
                'mem': 'Memory usage (percentage)',
                'rss': 'Physical memory usage(MB)',
                'vsz': 'Virtual memory usage (MB)',
                'threads': 'Number of threads(qtt)',
                'swap': 'Swap used(MB)',
            },
            dayfirst=True, includeColYlabel=True,
            cols_to_divide=['rss', 'vsz', 'swap'],
            division=1024
        )
        
        # -------------------------- IMAGE PROCESS
        PlottarGraficos().plottar(
            title="java",
            filename=dock_antigo['java'], 
            ylabel={
                'cpu': 'CPU usage (percentage)',
                'mem': 'Memory usage (percentage)',
                'rss': 'Physical memory usage(MB)',
                'vsz': 'Virtual memory usage (MB)',
                'threads': 'Number of threads(qtt)',
                'swap': 'Swap used(MB)',
            },
            dayfirst=True, includeColYlabel=True,
            cols_to_divide=['rss', 'vsz', 'swap'],
            division=1024
        )
        
        # PlottarGraficos().plottar(
        #     title="postgres_process",
        #     filename=dock_antigo['postgres_process'], 
        #     ylabel=labels(L_name=GRAPH_NAMES['postgres_process'], metrics='MB'),
        #     dayfirst=True, includeColYlabel=True,
        #     cols_to_divide=['rss', 'vsz', 'swap'],
        #     division=1024
        # )
        
        PlottarGraficos().plottar(
            title="beam.smp",
            filename=dock_antigo['beam.smp'], 
            ylabel={
                'cpu': 'CPU usage (percentage)',
                'mem': 'Memory usage (percentage)',
                'rss': 'Physical memory usage(MB)',
                'vsz': 'Virtual memory usage (MB)',
                'threads': 'Number of threads(qtt)',
                'swap': 'Swap used(MB)',
            },
            dayfirst=True, includeColYlabel=True,
            cols_to_divide=['rss', 'vsz', 'swap'],
            division=1024
        )
        
        PlottarGraficos().plottar(
            title="mysqld",
            filename=dock_antigo['mysqld'], 
            ylabel={
                'cpu': 'CPU usage (percentage)',
                'mem': 'Memory usage (percentage)',
                'rss': 'Physical memory usage(MB)',
                'vsz': 'Virtual memory usage (MB)',
                'threads': 'Number of threads(qtt)',
                'swap': 'Swap used(MB)',
            },
            dayfirst=True, includeColYlabel=True,
            cols_to_divide=['rss', 'vsz', 'swap'],
            division=1024
        )
        
        # PlottarGraficos().plottar(
        #     title="initdb",
        #     filename=dock_antigo['initdb'], 
        #     ylabel=labels(L_name=GRAPH_NAMES['initdb'], metrics='MB'),
        #     dayfirst=True, includeColYlabel=True,
        #     cols_to_divide=['rss', 'vsz', 'swap'],
        #     division=1024
        # )


    def docker_novo(self):
        dock_novo = Logs()
        # fragmentacao(MINIMUM_PROCESS_OCCURRENCES)
        # PlottarGraficos().plottar_fragmentation(PASTA_LOGS)
        
        # sys.exit(0)
        
        # PlottarGraficos().plottar(
        #     title="runs",
        #     filename=dock_novo['runs'], 
        #     ylabel='(percentage)', 
        #     dayfirst=True, includeColYlabel=True
        # )
        
        # --------------------- MACHINE RESOURCES
        PlottarGraficos().plottar(
            title="CPU",
            filename=dock_novo['cpu'], 
            ylabel='(percentage)', 
            dayfirst=True, includeColYlabel=True
        )

        PlottarGraficos().plottar(
            title="Memory Usage Over Time", 
            filename=dock_novo['memory'], 
            ylabel='Memory Usage (MB)', 
            dayfirst=True, 
            division=1024, includeColYlabel=True
        )
        
        PlottarGraficos().plottar(
            title="Disk Usage Over Time", 
            filename=dock_novo['disk'], 
            ylabel='Disk usage (GB)', 
            dayfirst=True, division=(1024**2)
        )

        PlottarGraficos().plottar(
            title="Zumbis", 
            filename=dock_novo['process'], 
            ylabel='Zumbis processes(qtt)', 
            dayfirst=True
        )

        # -------------------------- CONTAINER PROCESS
        PlottarGraficos().plottar(
            title="nginx",
            filename=dock_novo['nginx'], 
            ylabel='(seconds)', 
            dayfirst=True, includeColYlabel=True,
            division=1e+9
        )
        
        # PlottarGraficos().plottar(
        #     title="postgres",
        #     filename=dock_novo['postgres'], 
        #     ylabel='(seconds)', 
        #     dayfirst=True, includeColYlabel=True,
        #     division=1e+9
        # )
        
        PlottarGraficos().plottar(
            title="rabbitmq",
            filename=dock_novo['rabbitmq'], 
            ylabel='(seconds)', 
            dayfirst=True, includeColYlabel=True,
            division=1e+9
        )
        
        PlottarGraficos().plottar(
            title="redis",
            filename=dock_novo['redis'], 
            ylabel='(seconds)', 
            dayfirst=True, includeColYlabel=True,
            division=1e+9
        )
        
        # ----------------------------- DOCKER PROCESS
        PlottarGraficos().plottar(
            title="docker_novo - process",
            filename=dock_novo['docker'], 
            ylabel={
                'cpu': 'CPU usage (percentage)',
                'mem': 'Memory usage (percentage)',
                'rss': 'Physical memory usage(MB)',
                'vsz': 'Virtual memory usage (MB)',
                'threads': 'Number of threads(qtt)',
                'swap': 'Swap used(MB)',
            },
            dayfirst=True, includeColYlabel=True,
            cols_to_divide=['rss', 'vsz', 'swap'],
            division=1024
        )
        
        PlottarGraficos().plottar(
            title="dockerd_novo - process",
            filename=dock_novo['dockerd'], 
            ylabel={
                'cpu': 'CPU usage (percentage)',
                'mem': 'Memory usage (percentage)',
                'rss': 'Physical memory usage(MB)',
                'vsz': 'Virtual memory usage (MB)',
                'threads': 'Number of threads(qtt)',
                'swap': 'Swap used(MB)',
            },
            dayfirst=True, includeColYlabel=True,
            cols_to_divide=['rss', 'vsz', 'swap'],
            division=1024
        )
        
        PlottarGraficos().plottar(
            title="containerd_novo - process",
            filename=dock_novo['containerd'], 
            ylabel={
                'cpu': 'CPU usage (percentage)',
                'mem': 'Memory usage (percentage)',
                'rss': 'Physical memory usage(MB)',
                'vsz': 'Virtual memory usage (MB)',
                'threads': 'Number of threads(qtt)',
                'swap': 'Swap used(MB)',
            },
            dayfirst=True, includeColYlabel=True,
            cols_to_divide=['rss', 'vsz', 'swap'],
            division=1024
        )
        
        PlottarGraficos().plottar(
            title="containerd-shim_novo - process",
            filename=dock_novo['containerd-shim'], 
            ylabel={
                'cpu': 'CPU usage (percentage)',
                'mem': 'Memory usage (percentage)',
                'rss': 'Physical memory usage(MB)',
                'vsz': 'Virtual memory usage (MB)',
                'threads': 'Number of threads(qtt)',
                'swap': 'Swap used(MB)',
            },
            dayfirst=True, includeColYlabel=True,
            cols_to_divide=['rss', 'vsz', 'swap'],
            division=1024
        )
        
        PlottarGraficos().plottar(
            title="docker-proxy_novo - process",
            filename=dock_novo['docker-proxy'], 
            ylabel={
                'cpu': 'CPU usage (percentage)',
                'mem': 'Memory usage (percentage)',
                'rss': 'Physical memory usage(MB)',
                'vsz': 'Virtual memory usage (MB)',
                'threads': 'Number of threads(qtt)',
                'swap': 'Swap used(MB)',
            },
            dayfirst=True, includeColYlabel=True,
            cols_to_divide=['rss', 'vsz', 'swap'],
            division=1024
        )
        
        PlottarGraficos().plottar(
            title="runc_novo - process",
            filename=dock_novo['runc'], 
            ylabel={
                'cpu': 'CPU usage (percentage)',
                'mem': 'Memory usage (percentage)',
                'rss': 'Physical memory usage(MB)',
                'vsz': 'Virtual memory usage (MB)',
                'threads': 'Number of threads(qtt)',
                'swap': 'Swap used(MB)',
            },
            dayfirst=True, includeColYlabel=True,
            cols_to_divide=['rss', 'vsz', 'swap'],
            division=1024
        )
        
        # -------------------------- IMAGE PROCESS
        PlottarGraficos().plottar(
            title="java",
            filename=dock_novo['java'], 
            ylabel={
                'cpu': 'CPU usage (percentage)',
                'mem': 'Memory usage (percentage)',
                'rss': 'Physical memory usage(MB)',
                'vsz': 'Virtual memory usage (MB)',
                'threads': 'Number of threads(qtt)',
                'swap': 'Swap used(MB)',
            },
            dayfirst=True, includeColYlabel=True,
            cols_to_divide=['rss', 'vsz', 'swap'],
            division=1024
        )
        
        # PlottarGraficos().plottar(
        #     title="postgres_process",
        #     filename=dock_novo['postgres_process'], 
        #     ylabel=labels(L_name=GRAPH_NAMES['postgres_process'], metrics='MB'),
        #     dayfirst=True, includeColYlabel=True,
        #     cols_to_divide=['rss', 'vsz', 'swap'],
        #     division=1024
        # )
        
        PlottarGraficos().plottar(
            title="beam.smp",
            filename=dock_novo['beam.smp'], 
            ylabel={
                'cpu': 'CPU usage (percentage)',
                'mem': 'Memory usage (percentage)',
                'rss': 'Physical memory usage(MB)',
                'vsz': 'Virtual memory usage (MB)',
                'threads': 'Number of threads(qtt)',
                'swap': 'Swap used(MB)',
            },
            dayfirst=True, includeColYlabel=True,
            cols_to_divide=['rss', 'vsz', 'swap'],
            division=1024
        )
        
        PlottarGraficos().plottar(
            title="mysqld",
            filename=dock_novo['mysqld'], 
            ylabel={
                'cpu': 'CPU usage (percentage)',
                'mem': 'Memory usage (percentage)',
                'rss': 'Physical memory usage(MB)',
                'vsz': 'Virtual memory usage (MB)',
                'threads': 'Number of threads(qtt)',
                'swap': 'Swap used(MB)',
            },
            dayfirst=True, includeColYlabel=True,
            cols_to_divide=['rss', 'vsz', 'swap'],
            division=1024
        )
        
        # PlottarGraficos().plottar(
        #     title="initdb",
        #     filename=dock_novo['initdb'], 
        #     ylabel=labels(L_name=GRAPH_NAMES['initdb'], metrics='MB'),
        #     dayfirst=True, includeColYlabel=True,
        #     cols_to_divide=['rss', 'vsz', 'swap'],
        #     division=1024
        # )


    def podman(self):
        pod = Logs()
        # fragmentacao(MINIMUM_PROCESS_OCCURRENCES)
        # PlottarGraficos().plottar_fragmentation(PASTA_LOGS)
        
        # sys.exit(0)
        
        # PlottarGraficos().plottar(
        #     title="runs",
        #     filename=pod['runs'], 
        #     ylabel='(percentage)', 
        #     dayfirst=True, includeColYlabel=True
        # )
        
        # --------------------- MACHINE RESOURCES
        PlottarGraficos().plottar(
            title="CPU",
            filename=pod['cpu'], 
            ylabel='(percentage)', 
            dayfirst=True, includeColYlabel=True
        )

        PlottarGraficos().plottar(
            title="Memory Usage Over Time", 
            filename=pod['memory'], 
            ylabel='(GB)',
            dayfirst=True, 
            division=(1024**2), includeColYlabel=True
        )
        
        PlottarGraficos().plottar(
            title="Disk Usage Over Time", 
            filename=pod['disk'], 
            ylabel='Disk usage (GB)', 
            dayfirst=True, division=(1024**2)
        )
        
        PlottarGraficos().plottar(
            title="Zumbis", 
            filename=pod['process'], 
            ylabel='Zumbis processes(qtt)', 
            dayfirst=True
        )
        
        # -------------------------- CONTAINER PROCESS
        PlottarGraficos().plottar(
            title="nginx",
            filename=pod['nginx'], 
            ylabel='(seconds)', 
            dayfirst=True, includeColYlabel=True,
            division=1e+9
        )
        
        # PlottarGraficos().plottar(
        #     title="postgres",
        #     filename=pod['postgres'], 
        #     ylabel='(seconds)', 
        #     dayfirst=True, includeColYlabel=True,
        #     division=1e+9
        # )
        
        PlottarGraficos().plottar(
            title="rabbitmq",
            filename=pod['rabbitmq'], 
            ylabel='(seconds)', 
            dayfirst=True, includeColYlabel=True,
            division=1e+9
        )
        
        PlottarGraficos().plottar(
            title="redis",
            filename=pod['redis'], 
            ylabel='(seconds)', 
            dayfirst=True, includeColYlabel=True,
            division=1e+9
        )
        
        # ----------------------------- PODMAN PROCESS
        PlottarGraficos().plottar(
            title="podman",
            filename=pod['podman'], 
            ylabel={
                'cpu': 'CPU usage (percentage)',
                'mem': 'Memory usage (percentage)',
                'rss': 'Physical memory usage(MB)',
                'vsz': 'Virtual memory usage (MB)',
                'threads': 'Number of threads(qtt)',
                'swap': 'Swap used(MB)',
            },
            dayfirst=True, includeColYlabel=True,
            cols_to_divide=['rss', 'vsz', 'swap'],
            division=1024
        )
        
        PlottarGraficos().plottar(
            title="conmon",
            filename=pod['conmon'], 
            ylabel={
                'cpu': 'CPU usage (percentage)',
                'mem': 'Memory usage (percentage)',
                'rss': 'Physical memory usage(MB)',
                'vsz': 'Virtual memory usage (MB)',
                'threads': 'Number of threads(qtt)',
                'swap': 'Swap used(MB)',
            },
            dayfirst=True, includeColYlabel=True,
            cols_to_divide=['rss', 'vsz', 'swap'],
            division=1024
        )
        
        # PlottarGraficos().plottar(
        #     title="cron",
        #     filename=pod['cron'], 
        #     ylabel=labels(L_name=GRAPH_NAMES['cron'], metrics='MB'),
        #     dayfirst=True, includeColYlabel=True,
        #     cols_to_divide=['rss', 'vsz', 'swap'],
        #     division=1024
        # )
        
        PlottarGraficos().plottar(
            title="crun",
            filename=pod['crun'], 
            ylabel={
                'cpu': 'CPU usage (percentage)',
                'mem': 'Memory usage (percentage)',
                'rss': 'Physical memory usage(MB)',
                'vsz': 'Virtual memory usage (MB)',
                'threads': 'Number of threads(qtt)',
                'swap': 'Swap used(MB)',
            },
            dayfirst=True, includeColYlabel=True,
            cols_to_divide=['rss', 'vsz', 'swap'],
            division=1024
        )
        
        PlottarGraficos().plottar(
            title="systemd",
            filename=pod['systemd'], 
            ylabel={
                'cpu': 'CPU usage (percentage)',
                'mem': 'Memory usage (percentage)',
                'rss': 'Physical memory usage(MB)',
                'vsz': 'Virtual memory usage (MB)',
                'threads': 'Number of threads(qtt)',
                'swap': 'Swap used(MB)',
            },
            dayfirst=True, includeColYlabel=True,
            cols_to_divide=['rss', 'vsz', 'swap'],
            division=1024
        )
        
        # -------------------------- IMAGE PROCESS
        PlottarGraficos().plottar(
            title="java",
            filename=pod['java'], 
            ylabel={
                'cpu': 'CPU usage (percentage)',
                'mem': 'Memory usage (percentage)',
                'rss': 'Physical memory usage(MB)',
                'vsz': 'Virtual memory usage (MB)',
                'threads': 'Number of threads(qtt)',
                'swap': 'Swap used(MB)',
            },
            dayfirst=True, includeColYlabel=True,
            cols_to_divide=['rss', 'vsz', 'swap'],
            division=1024
        )
        
        # PlottarGraficos().plottar(
        #     title="postgres_process",
        #     filename=pod['postgres_process'], 
        #     ylabel=labels(L_name=GRAPH_NAMES['postgres_process'], metrics='MB'),
        #     dayfirst=True, includeColYlabel=True,
        #     cols_to_divide=['rss', 'vsz', 'swap'],
        #     division=1024
        # )
        
        PlottarGraficos().plottar(
            title="beam.smp",
            filename=pod['beam.smp'], 
            ylabel={
                'cpu': 'CPU usage (percentage)',
                'mem': 'Memory usage (percentage)',
                'rss': 'Physical memory usage(MB)',
                'vsz': 'Virtual memory usage (MB)',
                'threads': 'Number of threads(qtt)',
                'swap': 'Swap used(MB)',
            },
            dayfirst=True, includeColYlabel=True,
            cols_to_divide=['rss', 'vsz', 'swap'],
            division=1024
        )
        
        PlottarGraficos().plottar(
            title="mysqld",
            filename=pod['mysqld'], 
            ylabel={
                'cpu': 'CPU usage (percentage)',
                'mem': 'Memory usage (percentage)',
                'rss': 'Physical memory usage(MB)',
                'vsz': 'Virtual memory usage (MB)',
                'threads': 'Number of threads(qtt)',
                'swap': 'Swap used(MB)',
            },
            dayfirst=True, includeColYlabel=True,
            cols_to_divide=['rss', 'vsz', 'swap'],
            division=1024
        )
        
        # PlottarGraficos().plottar(
        #     title="initdb",
        #     filename=pod['initdb'], 
        #     ylabel=labels(L_name=GRAPH_NAMES['initdb'], metrics='MB'),
        #     dayfirst=True, includeColYlabel=True,
        #     cols_to_divide=['rss', 'vsz', 'swap'],
        #     division=1024
        # )