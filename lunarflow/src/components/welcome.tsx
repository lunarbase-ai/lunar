'use client'
import background from '@/assets/background_specific_need.svg'
import { BookOutlined, BulbOutlined, PlusOutlined, UnorderedListOutlined } from "@ant-design/icons"

const buttons = [
  { label: 'Use cases', href: '/home/demos', icon: <BulbOutlined /> },
  { label: 'New workflow', href: '/home/workflows', icon: <PlusOutlined /> },
  { label: 'Component Library', href: '/home/components', icon: <UnorderedListOutlined /> },
  { label: 'Documentation', href: 'https://lunarbase-ai.github.io/docs', icon: <BookOutlined /> },
]

const WelcomeCard = () => {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      gap: 8,
      paddingTop: 80,
      paddingBottom: 80,
      paddingRight: 16,
      paddingLeft: 16,
      backgroundColor: '#fafafa',
      backgroundImage: `url(${background.src})`,
      backgroundSize: 'cover',
      borderRadius: 16,
    }}>
      <h1
        style={{
          fontSize: 60,
          fontWeight: 'bold',
          color: '#0D181C',
          textAlign: 'center',
          marginBottom: 16,
        }}
      >
        Welcome to <span style={{ color: '#4DB1DD' }}>Lunar</span>
      </h1>
      <h4 style={{
        fontSize: 24,
        color: '#0d181c99',
        textAlign: 'center',
        fontWeight: '400',
        marginBottom: 32,
      }}>
        Have we met before? Here are a few options to get you started
      </h4>
      {/* <Image src={Logo} width={136} height={66} alt='Lunar' style={{ verticalAlign: 'middle' }} /> */}
      <div style={{
        display: 'flex',
        flexDirection: 'row',
        alignItems: 'center',
        flexWrap: 'wrap',
        paddingLeft: 16,
        paddingRight: 16,
        borderRadius: 8,
        gap: 16
      }}>
        {buttons.map(({ label, href, icon }) => <a
          key={href}
          href={href}
          style={{
            display: 'flex',
            flex: 1,
            justifyContent: 'center',
            alignItems: 'center',
            backgroundColor: '#4DB1DD',
            color: 'white',
            padding: 2,
            borderRadius: 8,
            textDecoration: 'none',
            flexGrow: 1,
            textAlign: 'center',
          }}>
          <div style={{
            fontSize: 15,
            fontWeight: 'bold',
            color: '#4DB1DD',
            width: '100%',
            padding: 16,
            whiteSpace: 'nowrap',
            backgroundColor: '#fafafa',
            borderRadius: 6,
          }}>
            <span style={{
              marginRight: 8,
            }}>{icon}</span>
            {label}
          </div>
        </a>
        )}
      </div>
    </div>
  )
}

export default WelcomeCard
