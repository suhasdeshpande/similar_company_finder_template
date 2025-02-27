from crewai_tools import ScrapeWebsiteTool, SerperDevTool

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class SimilarCompanyFinderTemplateCrew:
    """SimilarCompanyFinderTemplate crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def company_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["company_analyst"],
            tools=[SerperDevTool(), ScrapeWebsiteTool()],
            allow_delegation=False,
            verbose=True,
        )

    @agent
    def market_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["market_researcher"],
            tools=[SerperDevTool(), ScrapeWebsiteTool()],
            allow_delegation=False,
            verbose=True,
        )

    @agent
    def similarity_evaluator(self) -> Agent:
        return Agent(
            config=self.agents_config["similarity_evaluator"],
            tools=[],
            allow_delegation=False,
            verbose=True,
        )

    @agent
    def sales_strategist(self) -> Agent:
        return Agent(
            config=self.agents_config["sales_strategist"],
            tools=[],
            allow_delegation=False,
            verbose=True,
        )

    @task
    def analyze_target_company_task(self) -> Task:
        return Task(
            config=self.tasks_config["analyze_target_company_task"],
            agent=self.company_analyst(),
        )

    @task
    def find_potential_similar_companies_task(self) -> Task:
        return Task(
            config=self.tasks_config["find_potential_similar_companies_task"],
            agent=self.market_researcher(),
        )

    @task
    def evaluate_similarity_task(self) -> Task:
        return Task(
            config=self.tasks_config["evaluate_similarity_task"],
            agent=self.similarity_evaluator(),
            human_in_the_loop=True,
        )

    @task
    def develop_approach_recommendations_task(self) -> Task:
        return Task(
            config=self.tasks_config["develop_approach_recommendations_task"],
            agent=self.sales_strategist(),
            output_file="approach_recommendations.md",
        )

    @crew
    def crew(self) -> Crew:
        """Creates the SimilarCompanyFinderTemplate crew"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )

    # Example of how to run the crew with HITL webhook
    # def run_with_hitl(self, webhook_url):
    #     """Run the crew with Human-in-the-Loop enabled"""
    #     crew_instance = self.crew()
    #     result = crew_instance.kickoff(
    #         inputs={},  # Your inputs here
    #         webhook_url=webhook_url  # URL that will receive notifications when human input is needed
    #     )
    #     return result
