export interface ReportSection {
  key: string;
  title: string;
  icon: string;
  content: string;
}

export function buildReport(
studentName: string,
subject: string,
term: string)
: ReportSection[] {
  const first = studentName.split(' ')[0];
  return [
  {
    key: 'summary',
    title: 'Academic Summary',
    icon: 'GraduationCap',
    content: `Throughout ${term}, ${first} has engaged with ${subject} with growing independence and joy. ${first} chooses work purposefully during the morning cycle and sustains concentration for extended periods — a hallmark of the normalised Montessori child. Progress across foundational concepts has been steady and self-directed.`
  },
  {
    key: 'strengths',
    title: 'Learning Strengths',
    icon: 'Star',
    content: `${first} demonstrates remarkable focus and a natural curiosity for hands-on exploration. Fine-motor coordination is well developed, and ${first} readily returns to challenging works to master them. A strong sense of order supports independent completion of the full work cycle.`
  },
  {
    key: 'improvement',
    title: 'Areas for Growth',
    icon: 'Sprout',
    content: `${first} would benefit from broadening choices beyond preferred works, particularly in expressive language activities. Gentle invitations to group presentations will help build confidence in sharing ideas aloud with peers.`
  },
  {
    key: 'behaviour',
    title: 'Behaviour & Wellbeing',
    icon: 'Heart',
    content: `${first} is respectful of the prepared environment and of classmates, consistently caring for materials and returning them thoughtfully. Transitions are calm, and ${first} responds warmly to grace-and-courtesy lessons.`
  },
  {
    key: 'social',
    title: 'Social Skills & Collaboration',
    icon: 'Users',
    content: `${first} forms kind friendships and increasingly offers help to younger children — an emerging sign of leadership. Collaborative work is approached with patience and empathy.`
  },
  {
    key: 'creativity',
    title: 'Creativity & Critical Thinking',
    icon: 'Lightbulb',
    content: `${first} approaches open-ended work with imagination, often extending activities in original ways. Problem-solving is thoughtful; ${first} tests ideas, observes outcomes, and adapts — thinking like a young scientist.`
  },
  {
    key: 'activities',
    title: 'Suggested Activities',
    icon: 'ListChecks',
    content: `• Story-telling baskets to nurture expressive language\n• Nature journaling to extend observation skills\n• Simple group projects that invite gentle leadership\n• Continued practical-life works to reinforce independence`
  },
  {
    key: 'recommendations',
    title: 'Recommendations for Home',
    icon: 'Home',
    content: `Provide unhurried time for ${first} to explore interests deeply. Reading together daily and involving ${first} in real, purposeful home tasks (setting the table, watering plants) will beautifully reinforce classroom growth.`
  },
  {
    key: 'narrative',
    title: 'Overall Progress Narrative',
    icon: 'BookHeart',
    content: `${first} is flourishing. This term revealed a child growing in confidence, concentration, and kindness. We celebrate not a set of marks, but a joyful, capable learner discovering the world with wonder — and we look forward to walking alongside ${first} on the next part of the journey.`
  }];

}

export const competencyScores = [
{ label: 'Communication', value: 82 },
{ label: 'Social Skills', value: 88 },
{ label: 'Creativity', value: 90 },
{ label: 'Critical Thinking', value: 74 },
{ label: 'Leadership', value: 70 },
{ label: 'Participation', value: 85 }];