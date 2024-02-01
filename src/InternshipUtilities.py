import re
from datetime import datetime
import github
import discord
import json
import traceback

class InternshipUtilities:
    def __init__(self, repo: github.Repository.Repository, summer: bool, co_op: bool):
        self.repo = repo
        self.isSummer = summer 
        self.isCoop = co_op

    def binarySearchUS(self, state: str):
        US_STATES = [
            'AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA', 'HI',
            'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 'MI', 'MN',
            'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV', 'NY', 'OH',
            'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VA', 'VT', 'WA',
            'WI', 'WV', 'WY'
        ]
        low = 0
        high = len(US_STATES) - 1
        while low <= high:
            mid = low + (high - low) // 2
            if US_STATES[mid] == state:
                return True
            elif US_STATES[mid] > state:
                high = mid - 1
            else:
                low = mid + 1
        return False
    
    def getLinks(self):
        with open("./commits/repository_links_commits.json") as file:
            return json.load(file)

    async def getSummerInternships(self, channel : discord.TextChannel):
        try:
            current_month = datetime.now().strftime("%B")[:3]
            current_day = datetime.now().strftime("%d")
            current_year = datetime.now().strftime("%Y")
            check_duplicates = False

            date = f"{current_month} {current_day}"
            summer_internships = self.repo.get_contents(
                "README.md"
            ).decoded_content.decode("utf-8")

            job_postings = re.findall(
                rf"\|.*?{re.escape(date)}\s*\|", summer_internships
            )

            if len(job_postings) >= 1:
                data = self.getLinks()
                for job in job_postings:
                    # Grab the data and remove the empty elements
                    non_empty_elements = [
                        element.strip() for element in job.split("|") if element.strip()
                    ]

                    # Make sure that the position is still open
                    if "🔒" in non_empty_elements[3]:
                        continue
                    else:
                        job_link = re.search(
                            r'href="([^"]+)"', non_empty_elements[3]
                        ).group(1)

                    # Make sure that we aren't reposting jobs
                    if not check_duplicates:
                        if data["last_summer_internship_link"] == job_link:
                            break
                        else:
                            data["last_summer_internship_link"] = job_link

                        check_duplicates = True

                    # We need to check that the position is within the US and not remote
                    list_locations = []
                    if "<details>" in non_empty_elements[2]:
                        matches = re.findall(
                            r"([A-Za-z\s]+),\s([A-Z]{2})|\bRemote\b",
                            non_empty_elements[2],
                        )
                        for match in matches:
                            if match[0]:
                                city_state = ", ".join(match[:2])
                                list_locations.append(city_state)
                            else:
                                list_locations.append("Remote")
                    elif "</br>" in non_empty_elements[2]:
                        list_locations = non_empty_elements[2].split("</br>")

                    # If there are multiple locations, we need to populate the string correctly
                    if len(list_locations) > 1:
                        location = " | ".join(list_locations)
                    else:
                        is_remote = bool(
                            re.search(r"(?i)\bremote\b", non_empty_elements[2])
                        )
                        location = "Remote" if is_remote else non_empty_elements[2]

                        if location != "Remote":
                            match = re.search(r",\s*(.+)", location)
                            us_state = match.group(1) if match else None

                            if not us_state or not self.binarySearchUS(us_state):
                                continue

                    if "↳" not in non_empty_elements[0]:
                        match = re.search(r"\[([^\]]+)\]", non_empty_elements[0])
                        company_name = match.group(1) if match else "None"
                        previous_job_title = company_name
                    else:
                        company_name = previous_job_title

                    job_title = non_empty_elements[1]
                    date_posted = non_empty_elements[-1]

                    string = (
                        f"**📅 Date Posted:** {date_posted}\n"
                        f"**ℹ️ Company Name:** {company_name}\n"
                        f"**👨‍💻 Job Title:** {job_title}\n"
                        f"**📍 Location:** {location}\n"
                        f"**➡️  When?:** Summer {current_year}\n"
                        f"\n"
                        f"**👉 Job Link:** {job_link}\n"
                        f"\n"
                    )
                    await channel.send(string)
            
                # Save the updated data
                with open("./commits/repository_links_commits.json", "w") as file:
                    json.dump(data, file)
        except Exception as e:
            traceback.print_exc()
            raise e


        async def getCoopInternships(self, channel : discord.TextChannel):
            try:
                current_month = datetime.now().strftime("%B")[:3]
                current_day = datetime.now().strftime("%d")
                check_duplicates = False

                date = f"{current_month} {current_day}"
                co_op_internships = self.repo.get_contents(
                    "README-Off-Season.md"
                ).decoded_content.decode("utf-8")
                job_postings = re.findall(
                    rf"\|.*?{re.escape(date)}\s*\|", co_op_internships
                )

                if len(job_postings) >= 1:
                    data = self.getLinks()
                    for job in job_postings:
                        # Grab the data and remove the empty elements
                        non_empty_elements = [
                            element.strip() for element in job.split("|") if element.strip()
                        ]

                        # Make sure that the position is still open
                        if "🔒" in non_empty_elements[4]:
                            continue
                        else:
                            job_link = re.search(
                                r'href="([^"]+)"', non_empty_elements[4]
                            ).group(1)

                        # Make sure that we aren't reposting jobs
                        if not check_duplicates:
                            if data["last_co_op_internship_link"] == job_link:
                                break
                            else:
                                data["last_co_op_internship_link"] = job_link
                            check_duplicates = True

                        # We need to check that the position is within the US and not remote
                        list_locations = []
                        if "<details>" in non_empty_elements[2]:
                            matches = re.findall(
                                r"([A-Za-z\s]+),\s([A-Z]{2})|\bRemote\b",
                                non_empty_elements[2],
                            )
                            for match in matches:
                                if match[0]:
                                    city_state = ", ".join(match[:2])
                                    list_locations.append(city_state)
                                else:
                                    list_locations.append("Remote")
                        elif "</br>" in non_empty_elements[2]:
                            list_locations = non_empty_elements[2].split("</br>")

                        # If there are multiple locations, we need to populate the string correctly
                        if len(list_locations) > 1:
                            location = " | ".join(list_locations)
                        else:
                            is_remote = bool(
                                re.search(r"(?i)\bremote\b", non_empty_elements[2])
                            )
                            location = "Remote" if is_remote else non_empty_elements[2]

                            if location != "Remote":
                                match = re.search(r",\s*(.+)", location)
                                us_state = match.group(1) if match else None

                                if not us_state or not self.binarySearchUS(us_state):
                                    continue

                        if "↳" not in non_empty_elements[0]:
                            match = re.search(r"\[([^\]]+)\]", non_empty_elements[0])
                            company_name = match.group(1) if match else "None"
                            previous_job_title = company_name
                        else:
                            company_name = previous_job_title

                        job_title = non_empty_elements[1]
                        date_posted = non_empty_elements[-1]
                        terms = " |".join(non_empty_elements[3].split(","))

                        string = (
                            f"**📅 Date Posted:** {date_posted}\n"
                            f"**ℹ️ Company Name:** {company_name}\n"
                            f"**👨‍💻 Job Title:** {job_title}\n"
                            f"**📍 Location:** {location}\n"
                            f"**➡️  When?:**  {terms}\n"
                            f"\n"
                            f"**👉 Job Link:** {job_link}\n"
                            f"\n"
                        )
                        await channel.send(string)
                        
                    # Save the updated data
                    with open("./commits/repository_links_commits.json", "w") as file:
                        json.dump(data, file)
            except Exception as e:
                traceback.print_exc()
                raise e