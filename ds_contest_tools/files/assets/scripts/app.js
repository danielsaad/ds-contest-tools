// Parse query parameters from the current URL
const urlParams = new URLSearchParams(window.location.search);

// Get the value of each query parameter and store it in a variable
const testUrl = urlParams.get('id');
const expectedResultUrl = urlParams.get('expected-result');
const solutionUrl = urlParams.get('solution');
const veredictUrl = urlParams.get('veredict');
const checkerOutputUrl = urlParams.get('checker-output');
const execTimeUrl = urlParams.get('time');
const memoryUsageUrl = urlParams.get('memory');
const inputURL = urlParams.get('input');
const outputUrl = urlParams.get('output');
const ansUrl = urlParams.get('answer');
const reportLinkUrl = urlParams.get('report-link')

// Update the content of an HTML element with the value of a variable
const sourceName = document.getElementById('source-file');
sourceName.textContent = solutionUrl;

// Update the content of an HTML element with the value of a variable
const expectedResult = document.getElementById('expected-result');
expectedResult.textContent = expectedResultUrl;

// Update the content of an HTML element with the value of a variable
const testCase = document.getElementById('test');
testCase.textContent = testUrl;

// Update the content of an HTML element with the value of a variable
const veredict = document.getElementById('veredict');
veredict.textContent = veredictUrl;

// Update the content of an HTML element with the value of a variable
const checkerOutput = document.getElementById('checker-output');
checkerOutput.textContent = checkerOutputUrl;

// Update the content of an HTML element with the value of a variable
const execTime = document.getElementById('time');
execTime.textContent = execTimeUrl;

// Update the content of an HTML element with the value of a variable
const memoryUsage = document.getElementById('memory');
memoryUsage.textContent = memoryUsageUrl + ' KB';

// Update the href attribute of an HTML element with the value of a variable
const logoLink = document.getElementById('logo-link');
logoLink.setAttribute("href", reportLinkUrl)
const reportLink = document.getElementById('report-link');
reportLink.setAttribute("href", reportLinkUrl)


// Select an anchor element inside an HTML element, update its href 
// attribute with the value of a variable, and update its content with 
// the value of a variable
const inputLink = document.querySelector('#input a');
inputLink.href = inputURL;
inputLink.textContent = testUrl;

// Select an anchor element inside an HTML element, update its href 
// attribute with the value of a variable, and update its content with 
// the value of a variable
const outputLink = document.querySelector('#output a');
outputLink.href = outputUrl;
outputLink.textContent = testUrl;

// Select an anchor element inside an HTML element, update its href 
// attribute with the value of a variable, and update its content with 
// the value of a variable
const ansLink = document.querySelector('#answer a');
ansLink.href = ansUrl;
ansLink.textContent = testUrl;


