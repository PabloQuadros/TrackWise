import asyncio
from datetime import datetime, timedelta, time as dt_time
from src.repositories.search_scheduling_repository import SearchSchedulingRepository
from src.services.msc_service import MscService, get_msc_service 
from src.services.container_service import ContainerService
from src.repositories.container_repository import ContainerRepository
from src.mappers.container_mapper import ContainerMapper
from src.mappers.search_scheduling_mapper import SearchSchedulingMapper
from src.enums.SearchStatus import SearchStatus
from src.services.search_scheduling_service import SearchSchedulingService
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.enums.ShippingStatus import ShippingStatus

class ContainerSearchSchedulerService:
    def __init__(
            self, 
            scheduling_repository = SearchSchedulingRepository, 
            container_service = ContainerService, 
            msc_service = MscService, 
            container_repository = ContainerRepository,
            container_mapper = ContainerMapper,
            search_scheduling_service = SearchSchedulingService):
        self.scheduling_repository = scheduling_repository
        self.container_service = container_service
        self.msc_service = msc_service
        self.container_repository = container_repository
        self.container_mapper = container_mapper
        self.search_scheduling_service=search_scheduling_service

    def start_scheduler(self):
        scheduler = AsyncIOScheduler()
        # Roda a cada hora cheia
        scheduler.add_job(
            self.execute_search_routine_wrapper,
            'cron',  # tipo cron: baseado em hora/minuto/segundo
            minute=0
        )
        scheduler.start()
        print("[Scheduler] Agendador iniciado com rotina a cada hora cheia.")
    
    async def execute_search_routine_wrapper(self):
        now = datetime.now().replace(minute=0, second=0, microsecond=0)
        start = now
        end = now + timedelta(hours=1) - timedelta(seconds=1)

        print(f"[{datetime.now()}] Executando wrapper da rotina entre {start.time()} e {end.time()}")
        await self.execute_search_routine(start, end)
    
    async def execute_search_routine(self, start: datetime, end: datetime):
        try:
            print(f"\n[{datetime.now()}] Buscando containers agendados entre {start.time()} e {end.time()}")

            scheduling = await self.scheduling_repository.get()
            if not scheduling or not scheduling.containers:
                print("Nenhum agendamento encontrado para esta hora.")
                return

            containers_to_search = [
                cs for cs in scheduling.containers
                if start.time() <= cs.search_time <= end.time()
            ]
            containers_to_search.sort(key=lambda c: c.search_time)

            for container in containers_to_search:
                scheduled_time = datetime.combine(datetime.today(), container.search_time)
                now = datetime.now()
                wait_time = (scheduled_time - now).total_seconds()

                if wait_time > 0:
                    print(f"Aguardando {int(wait_time)}s para buscar container {container.container_number}")
                    await asyncio.sleep(wait_time)
                await self.search_single_container(container)

        except Exception as e:
            print(f"[{datetime.now()}] Erro inesperado ao executar rotina de busca: {e}")

    async def search_single_container(self, container):
        try:
            print(f"[{datetime.now().time()}] Executando busca para {container.container_number}")
            msc_response = await self.msc_service.get_tracking_info(container.container_number)
            actual_container = await self.container_repository.get_by_number(container.container_number)

            if msc_response.get("IsSuccess") is False:
                actual_container.add_search_log(SearchStatus.FAILURE)
                await self.container_repository.update(actual_container)
                print(f"[{datetime.now().time()}] Falha na busca de {container.container_number}")
                return

            new_container_data = self.container_mapper.from_api_response_to_dto_model(msc_response)

            updated_container = await self.container_service.compare_and_update_container(actual_container, new_container_data)
            if(updated_container.shipping_status.value == ShippingStatus.FINISHED.value):
                await self.search_scheduling_service.remove_container_schedule(updated_container.number)
        except Exception as e:
            print(f"[{datetime.now()}] Erro ao buscar container {container.container_number}: {e}")
            if actual_container:
                actual_container.add_search_log(SearchStatus.FAILURE)
                await self.container_repository.update(actual_container)

            
                
def get_container_search_scheduling_service() -> ContainerSearchSchedulerService:
    search_scheduling_mapper: SearchSchedulingMapper = SearchSchedulingMapper()
    search_scheduling_repository: SearchSchedulingRepository = SearchSchedulingRepository(search_scheduling_mapper)
    search_scheduling_service: SearchSchedulingService = SearchSchedulingService(search_scheduling_repository)
    msc_service: MscService = get_msc_service()
    container_mapper: ContainerMapper = ContainerMapper()
    container_repository: ContainerRepository = ContainerRepository(container_mapper)
    container_service: ContainerService = ContainerService(
        container_repository,
        container_mapper,
        msc_service,
        search_scheduling_service
    )

    return ContainerSearchSchedulerService(
        search_scheduling_repository,
        container_service,
        msc_service,
        container_repository,
        container_mapper,
        search_scheduling_service
    )