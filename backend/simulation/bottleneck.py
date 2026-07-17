def identify_bottleneck(

    technologies

):

    if not technologies:

        return None

    return max(

        technologies,

        key=lambda t: t["machines"]

    )