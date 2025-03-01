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
            human_input=True,
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
    def run_with_hitl(self, webhook_url=None):
        """Run the crew with Human-in-the-Loop enabled
        
        Note: In crewAI 0.76.2, webhook URLs are not directly supported.
        The human_input flag on tasks is used to enable human-in-the-loop functionality.
        This method includes a custom implementation to send notifications to a webhook URL.
        """
        import requests
        import threading
        
        # Make sure the evaluate_similarity_task has human_input=True
        crew_instance = self.crew()
        
        inputs = {
            "target_company": "<Placeholder Company>",
            "our_product": "<Placeholder Product>",
        }
        
        # Define a function to monitor for human input requests
        def monitor_for_human_input():
            import time
            # This is a simplified approach - in a real implementation, you would
            # need to hook into crewAI's event system or use a more sophisticated method
            print(f"Setting up webhook notification to: {webhook_url}")
            if webhook_url:
                try:
                    # Send a notification to the webhook URL
                    response = requests.post(
                        webhook_url,
                        json={
                            "message": "Human input required for SimilarCompanyFinderTemplate",
                            "timestamp": time.time(),
                            "status": "waiting_for_input"
                        }
                    )
                    print(f"Webhook notification sent. Response: {response.status_code}")
                except Exception as e:
                    print(f"Failed to send webhook notification: {e}")
        
        # Start the monitoring thread before kicking off the crew
        if webhook_url:
            threading.Thread(target=monitor_for_human_input).start()
        
        # Run the crew
        result = crew_instance.kickoff(inputs=inputs)
        
        # Send completion notification
        if webhook_url:
            try:
                requests.post(
                    webhook_url,
                    json={
                        "message": "SimilarCompanyFinderTemplate execution completed",
                        "timestamp": time.time(),
                        "status": "completed"
                    }
                )
            except Exception as e:
                print(f"Failed to send completion webhook notification: {e}")
        
        return result
