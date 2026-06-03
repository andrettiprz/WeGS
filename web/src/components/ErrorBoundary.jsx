import { Component } from 'react'
import { t } from '../lib/i18n'

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, info) {
    console.error('ErrorBoundary caught:', error, info)
  }

  render() {
    if (this.state.hasError) {
      return (
        <section className="section" style={{ paddingTop: '120px', textAlign: 'center' }}>
          <h2 style={{ color: 'var(--danger)', marginBottom: '1rem' }}>{t('error_title')}</h2>
          <p style={{ color: 'var(--text-dim)' }}>{t('error_text')}</p>
          <button
            onClick={() => { this.setState({ hasError: false }); window.location.reload() }}
            className="btn"
            style={{ marginTop: '1rem' }}
          >
            {t('error_reload')}
          </button>
        </section>
      )
    }
    return this.props.children
  }
}
