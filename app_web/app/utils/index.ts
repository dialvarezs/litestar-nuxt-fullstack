import { format, isValid, parseISO } from 'date-fns'

export function formatDatetime(value: string | null): string {
  const dt = parseISO(value ?? '')
  if (isValid(dt)) {
    return format(dt, 'dd/MM/yy HH:mm')
  }
  return ''
}

export function randomPassword(length: number = 12): string {
  const numbers = '1234567890'
  const lowercase = 'abcdefghijklmnopqrstuvwxyz'
  const uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
  const symbols = '!@#$%*_-+=:.'
  const allChars = numbers + lowercase + uppercase + symbols

  const getRandomChar = (str: string): string => {
    return str.charAt(Math.floor(Math.random() * str.length))
  }

  // Ensure the password contains at least one character from each category
  const passwordArray: string[] = [
    getRandomChar(numbers),
    getRandomChar(lowercase),
    getRandomChar(uppercase),
    getRandomChar(symbols),
  ]

  // Fill the rest of the password with random characters
  for (let i = passwordArray.length; i < length; i++) {
    passwordArray.push(getRandomChar(allChars))
  }

  // Flush the password array to ensure randomness
  return passwordArray
    .sort(() => Math.random() - 0.5)
    .join('')
}
