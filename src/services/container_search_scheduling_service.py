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

class ContainerSearchSchedulerService:
    def __init__(
            self, 
            scheduling_repository = SearchSchedulingRepository, 
            container_service = ContainerService, 
            msc_service = MscService, 
            container_repository = ContainerRepository,
            container_mapper = ContainerMapper):
        self.scheduling_repository = scheduling_repository
        self.container_service = container_service
        self.msc_service = msc_service
        self.container_repository = container_repository
        self.container_mapper = container_mapper

    async def start(self):
        while True:
            now = datetime.now()
            #minute=0,
            next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
            wait_seconds = (next_hour - now).total_seconds()
            print(f"[{now}] Aguardando {int(wait_seconds)} segundos até a próxima hora cheia...")
            await asyncio.sleep(wait_seconds)
            try:
                await self.execute_search_routine()
            except Exception as e:
                print(f"[{datetime.now()}] Erro ao executar rotina de busca: {e}")

    async def execute_search_routine(self):
        try:
            now = datetime.now()
            start = now.replace(minute=0, second=0, microsecond=0)
            end = start + timedelta(hours=1) - timedelta(seconds=1)

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
                await self._search_single_container(container)

        except Exception as e:
            print(f"[{datetime.now()}] Erro inesperado ao executar rotina de busca: {e}")

    async def _search_single_container(self, container):
        try:
            scheduled_time = datetime.combine(datetime.today(), container.search_time)
            now = datetime.now()
            wait_time = (scheduled_time - now).total_seconds()

            if wait_time > 0:
                print(f"Aguardando {int(wait_time)}s para buscar container {container.container_number}")
                await asyncio.sleep(wait_time)

            print(f"[{datetime.now().time()}] Executando busca para {container.container_number}")
            msc_response = await self.msc_service.get_tracking_info(container.container_number)
            actual_container = await self.container_repository.get_by_number(container.container_number)
            
            if msc_response.get("IsSuccess") is False:
                actual_container.add_search_log(SearchStatus.FAILURE)
                await self.container_repository.update(actual_container)
                print(f"[{datetime.now().time()}] Falha na busca de {container.container_number}")
                return

            new_container_data = self.container_mapper.from_api_response_to_domain_model(msc_response)
            actual_container.add_search_log(SearchStatus.SUCCESS)
            await self.container_repository.update(actual_container)

            changes = await self.container_service.compare_and_update_container(actual_container, new_container_data)
            if changes:
                for change in changes:
                    print(change)
            else:
                print("Nenhuma mudança detectada nas informações do contêiner.")
        except Exception as e:
            print(f"[{datetime.now()}] Erro ao buscar container {container.container_number}: {e}")

            
                
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
        container_mapper
    )