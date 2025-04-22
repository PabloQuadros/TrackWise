from typing import List
from src.domain.search_scheduling import SearchScheduling, ContainerSchedule
from src.repositories.search_scheduling_repository import SearchSchedulingRepository, get_search_scheduling_repository
from datetime import time
from fastapi import Depends

class SearchSchedulingService:
    def __init__(self, repository: SearchSchedulingRepository):
        self.repository = repository

    async def add_container_schedule(self, container_number: str) -> SearchScheduling:
        scheduling = await self.repository.get()
        
        if not scheduling:
            scheduling = SearchScheduling(
                start_search_time=time(8, 0, 0),
                end_search_time=time(20, 0, 0)
            )
            scheduling.add_container_schedule(ContainerSchedule(container_number, scheduling.start_search_time)),  # Primeiro container recebe 08:00
            await self.repository.save(scheduling)
            return scheduling
        
        # Se já existirem agendamentos, devemos calcular o novo horário
        new_search_time = self.calculate_next_search_time(scheduling)
        
        # Adiciona o novo container e seu horário de busca
        scheduling.add_container_schedule(ContainerSchedule(container_number, new_search_time))
        await self.repository.save(scheduling)
        
        return scheduling

    def calculate_next_search_time(self, scheduling: SearchScheduling) -> time:
        """Calcula o próximo horário de busca, seguindo as regras de alocação"""
        # Ordena os horários existentes
        sorted_times = sorted([container.search_time for container in scheduling.containers])
        # Se houver mais de dois horários, calcula o ponto médio entre os horários mais distantes
        if len(sorted_times) >= 2:
            max_gap_index = self.find_max_gap_index(sorted_times)
            new_search_time = self.calculate_mid_time(sorted_times[max_gap_index], sorted_times[max_gap_index + 1])
        else:
            # Caso contrário, entre os dois primeiros horários (08:00 e 20:00), aloca o ponto médio
            new_search_time = scheduling.end_search_time
        
        return new_search_time

    def find_max_gap_index(self, sorted_times: List[time]) -> int:
        """Encontra o índice do maior intervalo entre horários"""
        max_gap = 0
        max_gap_index = 0
        
        for i in range(len(sorted_times) - 1):
            gap = self.time_difference_in_seconds(sorted_times[i], sorted_times[i + 1])
            if gap > max_gap:
                max_gap = gap
                max_gap_index = i
        
        return max_gap_index

    def calculate_mid_time(self, start_time: time, end_time: time) -> time:
        """Calcula o ponto médio entre dois horários em segundos"""
        start_seconds = start_time.hour * 3600 + start_time.minute * 60 + start_time.second
        end_seconds = end_time.hour * 3600 + end_time.minute * 60 + end_time.second
        mid_seconds = (start_seconds + end_seconds) // 2

        hours = mid_seconds // 3600
        minutes = (mid_seconds % 3600) // 60
        seconds = mid_seconds % 60

        return time(hour=hours, minute=minutes, second=seconds)
    
    def time_difference_in_seconds(self, start_time: time, end_time: time) -> int:
        """Calcula a diferença em segundos entre dois horários"""
        start_seconds = start_time.hour * 3600 + start_time.minute * 60 + start_time.second
        end_seconds = end_time.hour * 3600 + end_time.minute * 60 + end_time.second
        return end_seconds - start_seconds

def get_search_scheduling_service(
    repository: SearchSchedulingRepository = Depends(get_search_scheduling_repository)
) -> SearchSchedulingService:
    return SearchSchedulingService(repository)