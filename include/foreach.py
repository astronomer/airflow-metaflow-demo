from metaflow import FlowSpec, step, environment

pod_env_vars={"AWS_ACCESS_KEY_ID": "admin", "AWS_SECRET_ACCESS_KEY": "adminadmin"}

class ForeachFlow(FlowSpec):

    @environment(pod_env_vars)
    @step
    def start(self):
        self.titles = ['Stranger Things',
                       'House of Cards',
                       'Narcos']
        self.next(self.a, foreach='titles')
    
    @environment(pod_env_vars)
    @step
    def a(self):
        self.title = '%s processed' % self.input
        self.next(self.join)

    @environment(pod_env_vars)
    @step
    def join(self, inputs):
        self.results = [input.title for input in inputs]
        self.next(self.end)

    @environment(pod_env_vars)
    @step
    def end(self):
        print('\n'.join(self.results))

if __name__ == '__main__':
    ForeachFlow()