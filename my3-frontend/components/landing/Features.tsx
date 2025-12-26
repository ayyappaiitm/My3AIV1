export function Features() {
  const features = [
    {
      title: 'Never Forget',
      description: 'Proactive reminders for birthdays, anniversaries, and special occasions.',
      icon: '🎂',
    },
    {
      title: 'Smart Recommendations',
      description: 'AI-powered gift suggestions tailored to each person\'s interests and preferences.',
      icon: '🎁',
    },
    {
      title: 'Relationship Network',
      description: 'Visualize and manage your relationships that matter most (up to 10).',
      icon: '🕸️',
    },
    {
      title: 'Conversation-First',
      description: 'Interact naturally with My3 through chat - no complex forms or menus.',
      icon: '💬',
    },
  ]

  return (
    <section className="py-20 px-4 bg-white">
      <div className="max-w-6xl mx-auto">
        <h2 className="text-4xl font-bold text-center mb-12 text-text">
          Why My3?
        </h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.map((feature, index) => (
            <div
              key={index}
              className="p-6 rounded-lg border border-gray-200 hover:shadow-lg transition-shadow"
            >
              <div className="text-4xl mb-4">{feature.icon}</div>
              <h3 className="text-xl font-semibold mb-2 text-text">
                {feature.title}
              </h3>
              <p className="text-text-light">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

