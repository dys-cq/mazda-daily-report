# Create streamlined project management workflows using database automations

- Source URL: https://www.notion.com/help/guides/create-streamlined-project-management-workflow-using-database-automations
- Captured At: 2026-03-12 08:56:01

## Original Content (Extract)

Product Notion Your AI workspace Notion Calendar Notion Mail Notion AI AI tools for work Agents Automate busywork AI Meeting Notes Perfectly written by AI Enterprise Search Find answers instantly Knowledge Base Centralize your knowledge Docs Simple and powerful Projects Manage any project Integrations Connect your apps Security Safe and scalable . See what’s new → Download the Notion App → AI AI features Notion AI AI tools for work Agents Automate busywork AI Meeting Notes Perfectly written by AI Enterprise Search Find answers instantly Explore use cases For work For life Solutions Teams Eng & Product Design Marketing IT Company size Startups Small businesses Enterprise Use Cases Education Personal Professional AI use cases Resources Browse Templates Consultants Integrations Discover What's New Customer stories Blog Webinars Learn Academy Product tours Help Enterprise Pricing Request a demo Log in Get Notion free Help Center Guides ← Guides Create streamlined project management workflows using database automations Database automations give you the power to create custom workflows handling the repetitive admin tasks of project management, so you’ll spend less time clicking buttons and more time on high-impact work. 10 min read Automations built into your database mean you can save time, simplify day-to-day work, and cut down on potential errors. In this guide How database automations save time and let you focus on the bigger picture Set up workflows for your tasks and projects Three automations for Notion Projects 1. Start a new task 2. Kick off a project 3. Send an email when a form is filled out Automate complexity away with formulas Getting started Setting up a formula-based automation More database automations for all your work As a project manager (or anyone who manages work), you might be inundated with repetitive tasks — updating project statuses, adding and assigning new tasks, sending out reminders, and so on, all the way from project kickoff to sign-off.

The manual workload increases as your team grows, but with Notion these tedious tasks can become database automations you set and forget.

In this guide, we’ll show you how to use database automations to set up custom workflows to streamline your processes and make sure nothing slips through the cracks.

How database automations save time and let you focus on the bigger picture Database automations consist of trigger events and the sequence of actions that follows. You’ll set up triggers and subsequent actions which are based on changes within database properties. The automation is structured as follows: “When any of these occur (a trigger), do this (an action).

So, for example, your trigger could be when a new page is added to the database, and the resulting actions might fill up some properties with your chosen responses.

Database automations can complete or update properties, add or edit pages in another database, send Slack notifications, and more. You can customize automations as needed and have several running in the same database for different scenarios.

While this feature is available in any Notion database, it’s uniquely powerful in the context of project management, where you need accurate workflows where nothing gets lost, missed, or forgotten.

By creating database automations, you can:

Reduce wasted time between tasks — Instead of your team members waiting around to be assigned their next project, they’ll be notified whenever something new lands on their plate.

Prevent human error — When your team is juggling multiple projects, it’s often the manual tasks (like re-assigning a task) that get forgotten. Setting up automations will reduce everyone’s cognitive load and prevent anything from getting missed.

Consolidate project management — Because database automations are native to Notion, you don’t need to create complex workflows using third-party tools. You can do all your project management in Notion to keep your team focused and reduce context-switching.

Database automations are only available on some plan types

You can set up database automations in a few simple steps.

Go to the options menu … and select Automations or just click on the lightning bolt icon.

Choose New automation and rename it if you wish.

Next, select your triggers, which can be when a new page is added, a certain property (or properties) are edited, or Any property is edited. Triggers are formatted as “or” statements, so if any one of the triggers occurs, the automation will occur.

Choose the resulting actions, such as adding a new page to this database or another database, editing a property (in this database or another), send a Slack notification.

Anytime you want to edit your automations, come back to the menu and make your changes.

Choose which pages your automation will apply to

You can also set up notifications to be sent to Gmail!

Ready to start building your own automations?

Here are some helpful examples to try out in your projects and tasks databases.

Every time you add a new task to your database, you can assign that task to someone, send them a notification, and give it the correct status.

To do this, create a new task and call it something like “New task flow”. Go to + Add trigger and select + Page added .

In the + Add action menu, give all new pages the status Not Started , and select a team member to assign them to. Finally, click Send Slack notification to and choose who you want to notify.

Now, whenever you add a new task, you’ll see all those properties are completed, and a Slack notification is sent.

To simplify the process of kicking off a project, you can create a Project kickoff automation in your Projects database.

The trigger will be when a project’s status is changed from Not started to Planning , and the actions that follow will automatically schedule a project kickoff meeting and notify the project manager.

In the Actions menu, select Add page to and find the meeting notes database. Call the new page Project Kickoff and click Edit another property to tag all team members and set the meeting date to Today , which will be the current date whenever the workflow is triggered. Finally, we can send a Slack notification to the project manager to alert them that the project is about to kick off.

3. Send an email when a form is filled out Imagine you have a company Help Desk database with a form that allows employees to submit requests directly. You want to notify the assignee every time someone fills out that form. Here's how to set this up in a few simple steps:

Click the lightning bolt icon and select + New automation

In the trigger section, choose Page added

From the list of actions, select Send mail to... and customize the email content

That's it! Now, whenever someone submits a new request, the assignee will receive an email notification. For more details on connecting Gmail, check out our help center article .

Use "@" to mention specific pages, people, or properties in email actions

Sometimes, simple "if-then" statements just don't cut it when you're trying to make your database sing. Let's say you want to set up an automation that assigns new bugs to the on-call engineer. Sounds simple, right? Well, here's where it gets a bit tricky — your on-call rotation is tracked in a separate database. Now you need to connect data from two different sources to make this work. It's not as straightforward as you might think — you might need to combine a few data points to kick off the final action.

This is where formula-based automations shine. They offer multiple ways to customize your task flow that wouldn't otherwise be possible. These automations can easily connect information from different databases or use date-specific variables (like date and time calculations) to streamline your workflow. The best part? You can focus on important work while Notion automatically handles the complex stuff—updating statuses, assigning tasks, or crunching numbers for reports.

Formula-based automations shine when it comes to creating custom actions that pull information from other pages or properties. They're also great for automations that need to read from different databases.

Here's how to set up a formula-based automation:

Click the lightning bolt icon at the top of your database.

After that, select Define variables to start configuring your formula-based automation.

Now that you're familiar with the basics, let's explore an example! Imagine you're running a company help desk and want to send a Gmail notification to your submitter every time your team resolves a ticket.

Set up your main trigger — First, make sure you have your main trigger set up. In this case, set your trigger to

Status as Complete . Then, enable an action every time the status is set to complete. To do this, head to the "Do" section and choose Send mail to from the actions list.

Add a personal touch to your Gmail notification

Add the formula-based automation — Click Add action and then Define variables to start building out your custom automation.

The goal of your formula is to: 1) let submitters know their ticket is resolved and 2) tell them when it was resolved. Here's a formula you could use:

"Your ticket" + Trigger page + "has been resolved at" + Time triggered

"Your ticket" — This kicks off our friendly message.

+ signs — These combine the different parts of our message.

Trigger page — This points to the specific ticket that started the automation.

"has been resolved at" — This gives context to what's happening.

Time triggered — This tells us when the ticket was closed.

You’re overall set up should look something like this:

And there you have it! When you put it all together, you get a warm, personal message. It lets the person who submitted the ticket know their issue is resolved and when it was taken care of.

It might take some practice, but once you get the hang of it, formula-based automations open up a world of possibilities. You can create more granular actions that grow with your workflow, saving you from clunky workarounds that eat up your time.

There are infinite ways to build efficient workflows across your entire workspace with database automations.

Here are more suggestions for ways to use database automations in your personal and professional life - with helpful templates to get started.

Add closing dates to your sales pipeline — When you mark a deal as Closed in your Sales Pipeline , automatically set the Date closed property to today, and send a notification to your #saleswins Slack channel.

Assign an interviewer for new candidates — In your company’s Applicant Tracker , an automation will tag the engineering team lead as Interviewer whenever you add a new candidate for the engineering team. You can create similar automations for other teams.

Mark courses you’re currently enrolled in — When you add a new course to the Courses database in your Assignment Tracker , the Currenty enrolled property will automatically be checked off.

Mark started and finished dates on your reading list — Complete Started and Completed dates for all books you read and organize in your Reading List .

Some of our templates have built-in automations — these are free for anyone to use. If you’re on a paid plan, you’ll be able to edit these automations according to your workflow.

Give Feedback Was this resource helpful? 👍 👎 Start with a template Browse over 10,000 templates in our template gallery

Visit the help center Subscribe on Youtube Chat with us Reference Docs Getting started Start here What is a block? Create a page Create a subpage What is a database? Create a database Start with a template Share your work Collaborate with people Badges & certifications See all Workspace & sidebar Intro to workspaces Navigate with the sidebar Manage your Library Create, join & leave workspaces Create, join & leave teamspaces Search in your workspace Home & My tasks Workspaces on mobile Delete a workspace See all Pa
